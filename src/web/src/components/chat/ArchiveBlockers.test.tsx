import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { ArchiveBlockers } from './ArchiveBlockers';

it('opens replacement review only from a compatibility blocker', () => {
  const review = vi.fn();
  render(<ArchiveBlockers items={[
    { id: 'REQ-0050', status: 'archive_requirement_conflict', message: '证明待核验' },
    { id: 'REQ-0050', status: 'missing_signoff', message: '待签署' },
  ] as any} onReviewReplacement={review} />);
  const action = screen.getByTestId('archive-review-replacement');
  expect(screen.getAllByTestId('archive-review-replacement')).toHaveLength(1);
  fireEvent.click(action);
  expect(review).toHaveBeenCalledOnce();
});
