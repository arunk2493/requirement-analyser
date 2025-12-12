import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import EpicCard from './EpicCard';

vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));

describe('EpicCard', () => {
  const mockEpic = {
    id: '1',
    title: 'Test Epic',
    description: 'Test Description',
  };

  it('renders without crashing', () => {
    const { container } = render(<EpicCard epic={mockEpic} />);
    expect(container).toBeInTheDocument();
  });

  it('renders card content', () => {
    const { container } = render(<EpicCard epic={mockEpic} />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<EpicCard epic={mockEpic} />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
