import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError, loginUser } from '@/api/client'
import { setToken } from '@/auth/token'
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

export default function LoginPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const registered = params.get('registered') === '1'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
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
    if (Object.keys(nextFieldErrors).length > 0) {
      setFieldErrors(nextFieldErrors)
      setBanner(null)
      return
    }

    setSubmitting(true)
    setBanner(null)
    setFieldErrors({})

    try {
      const data = await loginUser({
        email: email.trim(),
        password,
      })
      setToken(data.access_token)
      navigate('/')
    } catch (error) {
      if (error instanceof ApiError) {
        setFieldErrors(error.fieldErrors)
        setBanner(Object.keys(error.fieldErrors).length ? null : error.message)
      } else {
        setBanner('Could not log in. Try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-svh items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Log in</CardTitle>
          <CardDescription>
            {registered
              ? 'Account created. Sign in with the email and password you just used.'
              : 'Use the email and password from your account.'}
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
                autoComplete="current-password"
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
              {submitting ? 'Signing in…' : 'Log in'}
            </Button>
            <p className="text-sm text-muted-foreground">
              Need an account?{' '}
              <Link className="text-primary underline-offset-4 hover:underline" to="/register">
                Register
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
