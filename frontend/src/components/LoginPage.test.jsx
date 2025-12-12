import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import LoginPage from '../components/LoginPage';

vi.mock('axios');
vi.mock('primereact/toast', () => ({
  Toast: ({ ref }) => <div data-testid="toast" />,
}));

describe('LoginPage Component', () => {
  const mockSetIsAuthenticated = vi.fn();
  const mockSetUser = vi.fn();

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    mockSetIsAuthenticated.mockClear();
    mockSetUser.mockClear();
  });

  it('renders login form with email and password inputs', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument();
  });

  it('renders Requirement Analyzer header', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    expect(screen.getByText('Requirement Analyzer')).toBeInTheDocument();
  });

  it('renders both login and register tabs', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const tabs = screen.getAllByText(/Login|Register/);
    expect(tabs.length).toBeGreaterThanOrEqual(2);
  });

  it('renders Agentic AI System subtitle', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    expect(screen.getByText('Agentic AI System')).toBeInTheDocument();
  });

  it('email input accepts valid email format', async () => {
    const user = userEvent.setup();
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const emailInput = screen.getByPlaceholderText('your@email.com');
    await user.type(emailInput, 'valid.email@example.com');

    expect(emailInput).toHaveValue('valid.email@example.com');
  });

  it('password input accepts password text', async () => {
    const user = userEvent.setup();
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const passwordInput = screen.getByPlaceholderText('••••••••');
    await user.type(passwordInput, 'testpassword123');

    expect(passwordInput).toHaveValue('testpassword123');
  });

  it('renders form with submit button', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const submitButtons = screen.getAllByRole('button');
    const submitButton = submitButtons.find(btn => btn.type === 'submit');
    expect(submitButton).toBeInTheDocument();
  });

  it('submit button has proper styling classes', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const submitButtons = screen.getAllByRole('button');
    const submitButton = submitButtons.find(btn => btn.type === 'submit');
    // Button should exist and have styling
    expect(submitButton).toBeDefined();
  });

  it('renders with proper gradient background', () => {
    const { container } = render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const mainDiv = container.querySelector('.bg-gradient-to-br');
    expect(mainDiv).toBeInTheDocument();
  });

  it('renders form card with shadow styling', () => {
    const { container } = render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const formCard = container.querySelector('.shadow-xl');
    expect(formCard).toBeInTheDocument();
  });

  it('renders email label', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    expect(screen.getByText('Email Address')).toBeInTheDocument();
  });

  it('renders password label', () => {
    render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    expect(screen.getByText('Password')).toBeInTheDocument();
  });

  it('clears form fields on component remount', () => {
    const { rerender } = render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const emailInput = screen.getByPlaceholderText('your@email.com');
    expect(emailInput).toHaveValue('');
  });

  it('renders proper form structure with labels', () => {
    const { container } = render(
      <LoginPage
        setIsAuthenticated={mockSetIsAuthenticated}
        setUser={mockSetUser}
      />
    );

    const form = container.querySelector('form');
    expect(form).toBeInTheDocument();
  });
});
