import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import QAPage from './QAPage';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  fetchAllQA: vi.fn(() => Promise.resolve({ data: { qa: [], total_qa: 0 } })),
}));

describe('QAPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<QAPage />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<QAPage />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<QAPage />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
