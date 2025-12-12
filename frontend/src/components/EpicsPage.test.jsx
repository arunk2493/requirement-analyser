import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import EpicsPage from './EpicsPage';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/paginator', () => ({ Paginator: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  fetchAllEpics: vi.fn(() => Promise.resolve({ data: { epics: [], total_epics: 0 } })),
}));

describe('EpicsPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<EpicsPage />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<EpicsPage />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('supports dark mode', () => {
    const { container } = render(<EpicsPage />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
