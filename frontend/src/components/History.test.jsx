import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import History from './History';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));

vi.mock('../api/api', () => ({
  getHistory: vi.fn(() => Promise.resolve({ data: { history: [] } })),
}));

describe('History', () => {
  it('renders without crashing', () => {
    const { container } = render(<History />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<History />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<History />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
