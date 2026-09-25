import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

type ErrorBannerProps = {
  children: ReactNode
  className?: string
}

export function ErrorBanner({ children, className = '' }: ErrorBannerProps) {
  return (
    <p
      className={`rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive ${className}`}
      role="alert"
    >
      {children}
    </p>
  )
}

type EmptyStateProps = {
  children: ReactNode
  actionTo?: string
  actionLabel?: string
}

export function EmptyState({ children, actionTo, actionLabel }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
      <p>{children}</p>
      {actionTo && actionLabel ? (
        <Link className="mt-2 inline-block text-primary underline-offset-4 hover:underline" to={actionTo}>
          {actionLabel}
        </Link>
      ) : null}
    </div>
  )
}
