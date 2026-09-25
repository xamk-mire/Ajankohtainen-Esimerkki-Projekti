import { Link } from 'react-router-dom'
import type { UserPublic } from '@/api/client'
import { Button } from '@/components/ui/button'

type HeaderProps = {
  user: UserPublic
  onLogout: () => void
}

export default function Header({ user, onLogout }: HeaderProps) {
  const label = user.display_name.trim() || user.email

  return (
    <header className="flex items-center justify-between gap-4 border-b border-border px-6 py-3">
      <div className="flex items-center gap-6">
        <Link className="text-sm font-medium" to="/">
          Exercise Progress Tracker
        </Link>
        <nav className="flex items-center gap-4">
          <Link className="text-sm text-muted-foreground hover:text-foreground" to="/sessions">
            Sessions
          </Link>
          <Link className="text-sm text-muted-foreground hover:text-foreground" to="/plans">
            Plans
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-3">
        <span className="max-w-48 truncate text-sm text-muted-foreground" title={user.email}>
          {label}
        </span>
        <Button type="button" variant="outline" onClick={onLogout}>
          Log out
        </Button>
      </div>
    </header>
  )
}
