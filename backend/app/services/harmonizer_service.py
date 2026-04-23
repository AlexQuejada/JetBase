"""
Servicio de armonización de datos.
Detecta el archivo de referencia y alinea los demás a su esquema.
"""
import re
import pandas as pd
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class ColumnProfile:
    """Perfil de una columna: tipo estimado, patrones, completeness."""
    name: str
    estimated_type: str  # 'email', 'phone', 'date', 'number', 'text'
    valid_ratio: float   # 0.0 - 1.0, proporción de valores válidos
    null_ratio: float    # 0.0 - 1.0, proporción de nulos
    samples: List[str]   # Ejemplos de valores no-nulos


class HarmonizerService:
    """
    Armoniza múltiples DataFrames:
    - Detecta el archivo de referencia (mejor estructura)
    - Detecta y repara contenido en columnas incorrectas
    - Alinea esquemas de todos los archivos
    """

    # Patrones para detectar tipos de datos
    EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', re.IGNORECASE)
    PHONE_PATTERN = re.compile(r'^[\d\s\-\+\(\)\.]{7,20}$')
    DATE_PATTERNS = [
        re.compile(r'^\d{4}-\d{2}-\d{2}$'),           # 2024-01-15
        re.compile(r'^\d{2}/\d{2}/\d{4}$'),            # 15/01/2024
        re.compile(r'^\d{2}-\d{2}-\d{4}$'),            # 15-01-2024
        re.compile(r'^\d{2}\.\d{2}\.\d{4}$'),          # 15.01.2024
    ]
    NUMBER_PATTERN = re.compile(r'^-?\d+\.?\d*$')

    # Umbral para considerar contenido misplaced
    MISPLACED_THRESHOLD = 0.3  # 30% de valores que parecen pertenecer a otra columna

    @classmethod
    def profile_column(cls, series: pd.Series, col_name: str) -> ColumnProfile:
        """
        Analiza una columna y determina su perfil: tipo, calidad, ejemplos.
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return ColumnProfile(
                name=col_name,
                estimated_type='unknown',
                valid_ratio=0.0,
                null_ratio=1.0,
                samples=[]
            )

        # Convertir a string para análisis
        str_values = non_null.astype(str).str.strip()
        str_values = str_values[str_values != '']

        if len(str_values) == 0:
            return ColumnProfile(
                name=col_name,
                estimated_type='unknown',
                valid_ratio=0.0,
                null_ratio=1.0,
                samples=[]
            )

        # Clasificar tipo dominante
        type_counts = {'email': 0, 'phone': 0, 'date': 0, 'number': 0, 'text': 0}

        for val in str_values:
            if cls.EMAIL_PATTERN.match(val):
                type_counts['email'] += 1
            elif cls.PHONE_PATTERN.match(val):
                type_counts['phone'] += 1
            elif cls.NUMBER_PATTERN.match(val):
                type_counts['number'] += 1
            elif any(p.match(val) for p in cls.DATE_PATTERNS):
                type_counts['date'] += 1
            else:
                type_counts['text'] += 1

        dominant_type = max(type_counts, key=type_counts.get)
        valid_count = type_counts[dominant_type]
        valid_ratio = valid_count / len(str_values)

        return ColumnProfile(
            name=col_name,
            estimated_type=dominant_type,
            valid_ratio=valid_ratio,
            null_ratio=series.isna().mean(),
            samples=list(str_values.head(5))
        )

    @classmethod
    def calculate_file_health(cls, df: pd.DataFrame) -> float:
        """
        Calcula un score de 0-100 para la "salud" de un archivo.
        Considera: completitud, consistencia de tipos, estructura, cantidad de datos.
        """
        if df is None or df.empty:
            return 0.0

        score = 0.0

        # 1. Completitud global (25 puntos max)
        total_cells = df.size
        non_null_cells = df.count().sum()
        completeness = non_null_cells / total_cells if total_cells > 0 else 0
        score += completeness * 25

        # 2. Consistencia de tipos por columna (20 puntos max)
        if len(df.columns) > 0:
            type_consistency = 0
            for col in df.columns:
                profile = cls.profile_column(df[col], str(col))
                type_consistency += profile.valid_ratio
            score += (type_consistency / len(df.columns)) * 20

        # 3. Estructura - columnas con nombres válidos (20 puntos max)
        valid_names = 0
        for col in df.columns:
            col_str = str(col).strip().lower()
            if col_str and col_str not in ['nan', 'none', 'null', '', 'column_']:
                valid_names += 1
        score += (valid_names / len(df.columns)) * 20 if len(df.columns) > 0 else 0

        # 4. Riqueza de columnas - más columnas es mejor estructura (15 puntos max)
        # 4+ columnas se considera estructura completa
        col_richness = min(len(df.columns) / 4, 1.0)
        score += col_richness * 15

        # 5. Cantidad de datos (15 puntos max) - más filas es mejor
        # 10+ filas = 15 puntos, menos reduce score
        row_richness = min(df.shape[0] / 10, 1.0)
        score += row_richness * 15

        # 6. Filas completamente llenas (5 puntos max) - penalizar filas con muchos nulos
        if len(df) > 0:
            full_rows = (df.notna().sum(axis=1) == len(df.columns)).sum()
            full_row_ratio = full_rows / len(df)
            score += full_row_ratio * 5

        return score * 100  # Convertir a 0-100

    @classmethod
    def detect_misplaced_content(cls, df: pd.DataFrame) -> Dict[str, Dict[str, List[int]]]:
        """
        Detecta contenido misplaced: ej. emails en columna "nombre".
        Retorna dict: {columna_origen: {tipo_detectado: [indices_filas]}}
        """
        misplaced = {}

        for col in df.columns:
            profile = cls.profile_column(df[col], str(col))

            if profile.estimated_type == 'unknown' or profile.valid_ratio < 0.5:
                continue

            # Buscar si hay otra columna donde estos valores deberían estar
            for other_col in df.columns:
                if other_col == col:
                    continue

                other_profile = cls.profile_column(df[other_col], str(other_col))

                # Si la columna actual tiene tipo mejor que la otra,
                # y la otra tiene bajo ratio de ese tipo, hay candidacy
                type_score_current = profile.valid_ratio
                type_score_other = other_profile.valid_ratio

                # Buscar valores que coincidan con el tipo de otra columna
                candidates = []
                str_col = df[col].astype(str)

                for idx, val in str_col.items():
                    if pd.isna(val) or str(val).strip() == '':
                        continue

                    val_str = str(val).strip()

                    if profile.estimated_type == 'email' and cls.EMAIL_PATTERN.match(val_str):
                        candidates.append(idx)
                    elif profile.estimated_type == 'phone' and cls.PHONE_PATTERN.match(val_str):
                        candidates.append(idx)
                    elif profile.estimated_type == 'number' and cls.NUMBER_PATTERN.match(val_str):
                        candidates.append(idx)

                if len(candidates) > len(df) * cls.MISPLACED_THRESHOLD:
                    # Hay contenido misplaced significativo
                    if col not in misplaced:
                        misplaced[col] = {}
                    misplaced[col][profile.estimated_type] = candidates

        return misplaced

    @classmethod
    def choose_reference_file(cls, dataframes: List[pd.DataFrame], filenames: List[str]) -> Tuple[int, str]:
        """
        Elige el archivo de referencia basándose en el score de salud.
        Retorna (index, filename) del archivo elegido.
        """
        scores = []
        for i, df in enumerate(dataframes):
            score = cls.calculate_file_health(df)
            scores.append((i, score, filenames[i] if i < len(filenames) else f"file_{i}"))

        # Ordenar por score descendente
        scores.sort(key=lambda x: x[1], reverse=True)

        best = scores[0]
        return best[0], best[2]

    @classmethod
    def align_schema(
        cls,
        source_df: pd.DataFrame,
        reference_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Alinea el esquema de source_df al de reference_df:
        - Reordena columnas
        - Agrega columnas faltantes con NaN
        - Detecta y repara contenido misplaced
        """
        result = source_df.copy()

        # 1. Detectar contenido misplaced
        misplaced = cls.detect_misplaced_content(result)

        # 2. Obtener perfil de columnas del archivo referencia
        ref_profiles = {}
        for col in reference_df.columns:
            ref_profiles[col.lower().strip()] = cls.profile_column(
                reference_df[col], col
            )

        # 3. Para cada columna misplaced, intentar reasignar
        for source_col, type_info in misplaced.items():
            for detected_type, row_indices in type_info.items():
                # Buscar columna en referencia que espera este tipo
                target_col = None
                for ref_col_name, ref_profile in ref_profiles.items():
                    if ref_profile.estimated_type == detected_type:
                        target_col = ref_col_name
                        break

                if target_col and target_col != source_col.lower().strip():
                    # Buscar el nombre exacto con el case correcto
                    target_col_exact = None
                    for c in result.columns:
                        if c.lower().strip() == target_col:
                            target_col_exact = c
                            break

                    if target_col_exact and target_col_exact != source_col:
                        # Forzar dtype object para evitar errores de conversion
                        result[target_col_exact] = result[target_col_exact].astype(object)
                        result[source_col] = result[source_col].astype(object)

                        for idx in row_indices:
                            val = result.loc[idx, source_col]
                            if pd.isna(val):
                                continue

                            val_str = str(val).strip()
                            is_valid_for_type = False

                            if detected_type == 'email' and cls.EMAIL_PATTERN.match(val_str):
                                is_valid_for_type = True
                            elif detected_type == 'phone' and cls.PHONE_PATTERN.match(val_str):
                                is_valid_for_type = True
                            elif detected_type == 'number' and cls.NUMBER_PATTERN.match(val_str):
                                is_valid_for_type = True

                            if is_valid_for_type:
                                # Mover el valor a la columna correcta
                                result.loc[idx, target_col_exact] = val
                                # Limpiar la columna origen
                                result.loc[idx, source_col] = np.nan

        # 4. Reordenar columnas al esquema del referencia
        ref_col_names = list(reference_df.columns)
        existing_cols = [c for c in ref_col_names if c in result.columns]
        extra_cols = [c for c in result.columns if c not in ref_col_names]
        result = result[existing_cols + extra_cols]

        # 5. Agregar columnas faltantes
        for col in ref_col_names:
            if col not in result.columns:
                result[col] = np.nan

        # Reordenar de nuevo con las nuevas columnas
        result = result[ref_col_names]

        return result

    @classmethod
    def harmonize(
        cls,
        dataframes: List[pd.DataFrame],
        filenames: List[str]
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Armoniza múltiples DataFrames:
        1. Detecta el archivo de referencia (mejor salud)
        2. Alinea todos los archivos al esquema del referencia
        3. Combina en un solo DataFrame

        Returns:
            (DataFrame armonizado, metadata del proceso)
        """
        # Single file: return as-is with metadata
        if len(dataframes) == 1:
            df = dataframes[0]
            scores = [{
                'index': 0,
                'filename': filenames[0] if filenames else "file_0",
                'health_score': cls.calculate_file_health(df),
                'rows': len(df),
                'columns': len(df.columns)
            }]
            metadata = {
                'reference_file': filenames[0] if filenames else "file_0",
                'reference_index': 0,
                'file_scores': scores,
                'files_harmonized': 1,
                'combined_rows': len(df),
                'final_columns': list(df.columns)
            }
            return df, metadata

        if len(dataframes) < 2:
            raise ValueError("Se necesitan al menos 2 archivos para armonizar")

        # Calcular scores
        scores = []
        for i, df in enumerate(dataframes):
            scores.append({
                'index': i,
                'filename': filenames[i] if i < len(filenames) else f"file_{i}",
                'health_score': cls.calculate_file_health(df),
                'rows': len(df),
                'columns': len(df.columns)
            })

        # Elegir referencia (el de mayor score)
        reference_idx, reference_name = cls.choose_reference_file(dataframes, filenames)
        reference_df = dataframes[reference_idx]

        metadata = {
            'reference_file': reference_name,
            'reference_index': reference_idx,
            'file_scores': scores,
            'files_harmonized': len(dataframes)
        }

        # Alineación de cada archivo al esquema del referencia
        aligned_dfs = []
        for i, df in enumerate(dataframes):
            if i == reference_idx:
                aligned_dfs.append(reference_df.copy())
            else:
                aligned_df = cls.align_schema(df, reference_df)
                aligned_dfs.append(aligned_df)

        # Combinar verticalmente (union)
        combined = pd.concat(aligned_dfs, ignore_index=True)

        # Agregar columna de trazabilidad
        source_col = []
        for df, fname in zip(dataframes, filenames):
            source_col.extend([fname] * len(df))
        combined['__source_file__'] = source_col

        metadata['combined_rows'] = len(combined)
        metadata['final_columns'] = list(combined.columns)

        return combined, metadata