// Staff status moves offered per status. The server's state machine (app/domain/workflow.py) is the
// authority and rejects anything else; this list only decides which buttons to show.

import type { Status } from '../../api';
import type { MessageKey } from '../../i18n';

export interface Move { to: Status; label: MessageKey; reason: boolean; danger?: boolean }

const M = (to: Status, label: MessageKey, reason = false, danger = false): Move => ({ to, label, reason, danger });

export const STAFF_MOVES: Partial<Record<Status, Move[]>> = {
  submitted: [M('under_review', 'case.move.startReview'), M('rejected', 'case.move.reject', true, true)],
  under_review: [M('on_hold', 'case.move.hold', true), M('rejected', 'case.move.reject', true, true)],
  assigned: [M('in_progress', 'case.move.startWork'), M('on_hold', 'case.move.hold', true)],
  in_progress: [M('on_hold', 'case.move.hold', true)],
  on_hold: [M('in_progress', 'case.move.resume')],
  awaiting_resident: [M('in_progress', 'case.move.resumeWithoutReply')],
  reopened: [M('in_progress', 'case.move.startWork')],
};

export const movesFor = (s: Status): Move[] => STAFF_MOVES[s] ?? [];

/** Staff may mark work resolved from these statuses (with a note the resident sees). */
export const RESOLVABLE: Status[] = ['assigned', 'in_progress', 'reopened'];
export const canResolve = (s: Status) => RESOLVABLE.includes(s);
