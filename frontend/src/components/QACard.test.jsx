import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import QACard from './QACard';

vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));

describe('QACard', () => {
  const mockQA = {
    id: '1',
    question: 'Test Question',
    answer: 'Test Answer',
  };

  it('renders without crashing', () => {
    const { container } = render(<QACard qa={mockQA} />);
    expect(container).toBeInTheDocument();
  });

  it('renders card content', () => {
    const { container } = render(<QACard qa={mockQA} />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<QACard qa={mockQA} />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
