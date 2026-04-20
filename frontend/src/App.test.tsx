import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Flintrex app', () => {
    render(<App />);
    const linkElement = screen.getByText(/Flintrex/i);
    expect(linkElement).toBeInTheDocument();
});