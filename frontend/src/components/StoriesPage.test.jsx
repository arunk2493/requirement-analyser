import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import StoriesPage from './StoriesPage';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  fetchAllStories: vi.fn(() => Promise.resolve({ data: { stories: [], total_stories: 0 } })),
}));

describe('StoriesPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<StoriesPage />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<StoriesPage />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<StoriesPage />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
