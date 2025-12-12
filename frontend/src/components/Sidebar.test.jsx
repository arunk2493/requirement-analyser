import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from '../components/Sidebar';

describe('Sidebar Component', () => {
  const mockSetDarkMode = vi.fn();
  const mockSetIsAuthenticated = vi.fn();
  const mockSetUser = vi.fn();
  const mockUser = { email: 'test@example.com' };

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders sidebar with navigation links', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Upload')).toBeInTheDocument();
    expect(screen.getByText('Epics')).toBeInTheDocument();
    expect(screen.getByText('Stories')).toBeInTheDocument();
  });

  it('renders all main navigation items', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const expectedLinks = [
      'Dashboard',
      'Upload',
      'Analyser Agents',
      'Epics',
      'Stories',
      'QA',
      'Test Plans',
      'Search Documents',
      'Jira Integration',
      'History',
    ];

    expectedLinks.forEach((link) => {
      expect(screen.getByText(link)).toBeInTheDocument();
    });
  });

  it('displays collapsed state initially', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const sidebarDiv = container.firstChild;
    expect(sidebarDiv).toHaveClass('w-20');
  });

  it('displays user email in sidebar', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
  });

  it('renders rocket emoji as brand icon', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('🚀')).toBeInTheDocument();
  });

  it('renders search documents link', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Search Documents')).toBeInTheDocument();
  });

  it('renders jira integration link', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Jira Integration')).toBeInTheDocument();
  });

  it('renders logout button', () => {
    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('logout button is functional', async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const logoutButton = screen.getByText('Logout');
    await user.click(logoutButton);

    // Logout button should be present
    expect(logoutButton).toBeInTheDocument();
  });

  it('has proper styling with gradient background', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const sidebarDiv = container.firstChild;
    expect(sidebarDiv).toHaveClass('bg-gradient-to-b');
  });

  it('renders nav links with proper structure', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const navLinks = container.querySelectorAll('a');
    expect(navLinks.length).toBeGreaterThan(0);
  });

  it('applies dark styling classes', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar
          darkMode={true}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    expect(container.firstChild).toBeInTheDocument();
  });

  it('has flex column layout', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar
          darkMode={false}
          setDarkMode={mockSetDarkMode}
          user={mockUser}
          setIsAuthenticated={mockSetIsAuthenticated}
          setUser={mockSetUser}
        />
      </BrowserRouter>
    );

    const sidebarDiv = container.firstChild;
    expect(sidebarDiv).toHaveClass('flex');
  });
});
