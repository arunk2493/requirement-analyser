import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import StoryCard from './StoryCard';

vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));

describe('StoryCard', () => {
  const mockStory = {
    id: '1',
    title: 'Test Story',
    description: 'Test Description',
  };

  it('renders without crashing', () => {
    const { container } = render(<StoryCard story={mockStory} />);
    expect(container).toBeInTheDocument();
  });

  it('renders card content', () => {
    const { container } = render(<StoryCard story={mockStory} />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<StoryCard story={mockStory} />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
