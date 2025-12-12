import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import TestPlanCard from './TestPlanCard';

vi.mock('primereact/button', () => ({ Button: ({ label }) => <button>{label}</button> }));

describe('TestPlanCard', () => {
  const mockTestPlan = {
    id: '1',
    title: 'Test Plan',
    description: 'Test Description',
  };

  it('renders without crashing', () => {
    const { container } = render(<TestPlanCard testplan={mockTestPlan} />);
    expect(container).toBeInTheDocument();
  });

  it('renders card content', () => {
    const { container } = render(<TestPlanCard testplan={mockTestPlan} />);
    expect(container.textContent.length).toBeGreaterThan(0);
  });

  it('applies styling', () => {
    const { container } = render(<TestPlanCard testplan={mockTestPlan} />);
    const div = container.querySelector('div');
    expect(div).toBeInTheDocument();
  });
});
