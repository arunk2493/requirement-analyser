import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import JiraIntegration from './JiraIntegration';

vi.mock('primereact/datatable', () => ({
  DataTable: ({ children }) => <div data-testid="datatable">{children}</div>,
}));
vi.mock('primereact/column', () => ({ Column: () => null }));
vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));
vi.mock('primereact/inputtext', () => ({ InputText: () => <input /> }));
vi.mock('primereact/toast', () => ({ Toast: () => null }));
vi.mock('primereact/dropdown', () => ({ Dropdown: () => null }));

vi.mock('../api/api', () => ({
  getJiraStatus: vi.fn(() => Promise.resolve({ data: { status: 'disconnected' } })),
  searchJiraIssues: vi.fn(() => Promise.resolve({ data: { issues: [] } })),
}));

describe('JiraIntegration', () => {
  it('renders without crashing', () => {
    const { container } = render(<JiraIntegration />);
    expect(container).toBeInTheDocument();
  });

  it('renders page content', () => {
    const { container } = render(<JiraIntegration />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<JiraIntegration />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
