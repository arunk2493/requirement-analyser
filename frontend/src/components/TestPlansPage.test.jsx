import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import TestPlansPage from './TestPlansPage';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  fetchAllTestPlans: vi.fn(() => Promise.resolve({ data: { testplans: [], total_testplans: 0 } })),
}));

describe('TestPlansPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<TestPlansPage />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<TestPlansPage />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<TestPlansPage />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
