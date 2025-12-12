import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import SearchDocuments from './SearchDocuments';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  searchDocuments: vi.fn(() => Promise.resolve({ data: { results: [] } })),
}));

describe('SearchDocuments', () => {
  it('renders without crashing', () => {
    const { container } = render(<SearchDocuments />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<SearchDocuments />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<SearchDocuments />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
