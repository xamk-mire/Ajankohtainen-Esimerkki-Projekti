import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError, registerUser } from '@/api/client'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-50'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [banner, setBanner] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const nextFieldErrors: Record<string, string> = {}
    if (!email.trim()) {
      nextFieldErrors.email = 'Email is required'
    }
    if (!password) {
      nextFieldErrors.password = 'Password is required'
    }
    if (!displayName.trim()) {
      nextFieldErrors.display_name = 'Display name is required'
    }
    if (Object.keys(nextFieldErrors).length > 0) {
      setFieldErrors(nextFieldErrors)
      setBanner(null)
      return
    }

    setSubmitting(true)
    setBanner(null)
    setFieldErrors({})

    try {
      await registerUser({
        email: email.trim(),
        password,
        display_name: displayName.trim(),
      })
      // Register returns a public user, not a JWT — go to Login (S2-15).
      navigate('/login?registered=1')
    } catch (error) {
      if (error instanceof ApiError) {
        setFieldErrors(error.fieldErrors)
        setBanner(Object.keys(error.fieldErrors).length ? null : error.message)
      } else {
        setBanner('Could not register. Try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-svh items-center justify-center bg-background p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Create an account</CardTitle>
          <CardDescription>
            After you register you will be sent to Login. The API does not issue
            a token on register.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit} noValidate>
            {banner ? (
              <p
                className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive"
                role="alert"
              >
                {banner}
              </p>
            ) : null}
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Display name
              <input
                className={inputClassName}
                autoComplete="name"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                disabled={submitting}
                aria-invalid={Boolean(fieldErrors.display_name)}
              />
              {fieldErrors.display_name ? (
                <span className="font-normal text-destructive">
                  {fieldErrors.display_name}
                </span>
              ) : null}
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Email
              <input
                className={inputClassName}
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={submitting}
                aria-invalid={Boolean(fieldErrors.email)}
              />
              {fieldErrors.email ? (
                <span className="font-normal text-destructive">
                  {fieldErrors.email}
                </span>
              ) : null}
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Password
              <input
                className={inputClassName}
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={submitting}
                aria-invalid={Boolean(fieldErrors.password)}
              />
              {fieldErrors.password ? (
                <span className="font-normal text-destructive">
                  {fieldErrors.password}
                </span>
              ) : null}
            </label>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Creating account…' : 'Register'}
            </Button>
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link className="text-primary underline-offset-4 hover:underline" to="/login">
                Log in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
