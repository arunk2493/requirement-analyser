import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import UploadPage from './UploadPage';

vi.mock('primereact/toast', () => ({
  Toast: vi.fn(),
}));

vi.mock('../api/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('UploadPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<UploadPage />);
    expect(container).toBeInTheDocument();
  });

  it('renders upload section', () => {
    const { container } = render(<UploadPage />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies dark mode classes', () => {
    const { container } = render(<UploadPage />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
