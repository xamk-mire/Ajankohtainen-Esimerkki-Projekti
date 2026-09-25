/** Cache keys for TanStack Query. Later pages should import these helpers. */

export type SessionListFilters = {
  from?: string | null
  to?: string | null
  status?: string | null
  activityTypeId?: string | null
  unscheduled?: boolean | null
  planId?: string | null
}

export const queryKeys = {
  health: ['health'] as const,
  sessions: (filters: SessionListFilters = {}) => ['sessions', filters] as const,
  plans: ['plans'] as const,
  plan: (id: string) => ['plans', id] as const,
  calendar: (from: string | null, to: string | null, planId: string | null) =>
    ['calendar', from, to, planId] as const,
}
