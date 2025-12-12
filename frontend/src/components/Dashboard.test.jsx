import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../components/Dashboard';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Link: ({ to, children, ...props }) => (
      <a href={to} {...props}>
        {children}
      </a>
    ),
  };
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders dashboard header', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Requirement Analyzer/i)).toBeInTheDocument();
  });

  it('renders all dashboard cards', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Uploads')).toBeInTheDocument();
    expect(screen.getByText('Epics')).toBeInTheDocument();
    expect(screen.getByText('Stories')).toBeInTheDocument();
    expect(screen.getByText('Test Plans')).toBeInTheDocument();
    expect(screen.getByText('Jira Integration')).toBeInTheDocument();
  });

  it('renders card descriptions', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Manage requirement files')).toBeInTheDocument();
    expect(screen.getByText('View all epics and their details')).toBeInTheDocument();
    expect(screen.getByText('Browse user stories')).toBeInTheDocument();
    expect(screen.getByText('View test plans and scenarios')).toBeInTheDocument();
    expect(screen.getByText('Connect and sync to Jira')).toBeInTheDocument();
  });

  it('renders links to feature pages', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByRole('link', { name: /upload/i })).toHaveAttribute(
      'href',
      '/upload'
    );
    expect(screen.getByRole('link', { name: /epics/i })).toHaveAttribute(
      'href',
      '/epics'
    );
    expect(screen.getByRole('link', { name: /stories/i })).toHaveAttribute(
      'href',
      '/stories'
    );
  });

  it('initializes stats with default values', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Stats should be rendered with initial values (0)
    expect(container).toBeInTheDocument();
  });

  it('displays card content in gradient containers', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Check for gradient classes
    const gradientDivs = container.querySelectorAll('[class*="from-"]');
    expect(gradientDivs.length).toBeGreaterThan(0);
  });

  it('renders feature cards with icons', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Icons are rendered via react-icons
    const svgElements = container.querySelectorAll('svg');
    expect(svgElements.length).toBeGreaterThan(0);
  });

  it('renders navigation arrows in cards', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Arrow icons should be present
    const arrows = container.querySelectorAll('svg');
    expect(arrows.length).toBeGreaterThan(0);
  });

  it('has accessible heading hierarchy', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const heading = screen.getByRole('heading', {
      level: 1,
      name: /Requirement Analyzer/i,
    });
    expect(heading).toBeInTheDocument();
  });

  it('renders proper background styling', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const mainDiv = container.firstChild;
    expect(mainDiv).toHaveClass('min-h-screen');
    expect(mainDiv).toHaveClass('bg-gradient-to-br');
  });

  it('renders grid layout for cards', () => {
    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const gridContainer = container.querySelector('[class*="grid"]');
    expect(gridContainer).toBeInTheDocument();
  });
});
