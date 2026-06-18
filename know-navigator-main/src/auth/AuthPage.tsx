import { useState } from "react";
import { supabase } from "@/services/supabase";
import { toast } from "sonner";
import { BookOpen, Lock, Mail, ArrowRight, Loader2, AlertCircle } from "lucide-react";

export function AuthPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [infoMsg, setInfoMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setInfoMsg("");
    if (!email.trim() || !password.trim()) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    setLoading(true);

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;

        if (data.session) {
          toast.success("Account created!");
        } else {
          // Email confirmation required
          setInfoMsg("Check your email for a confirmation link, then sign in.");
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        toast.success("Welcome back!");
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: window.location.origin,
        },
      });
      if (error) throw error;
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Google Sign-In failed.");
    }
  };

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-background px-4">
      {/* Moving aurora background */}
      <div className="aurora pointer-events-none absolute inset-0 opacity-60" />

      <div className="relative z-10 w-full max-w-md overflow-hidden rounded-2xl border border-border/80 bg-surface/40 p-8 glass-strong shadow-elegant">
        {/* Brand */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="grid h-12 w-12 place-items-center rounded-2xl brand-gradient shadow-[0_0_20px_-4px_var(--color-primary)] mb-4">
            <BookOpen className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {isSignUp ? "Create your account" : "Sign in to Research"}
          </h1>
          <p className="mt-2 text-xs text-muted-foreground">
            Wikipedia AI-Powered Assistant with Cited Sources
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Email address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                disabled={loading}
                className="w-full rounded-lg border border-border bg-background/50 py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30 disabled:opacity-55"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                disabled={loading}
                className="w-full rounded-lg border border-border bg-background/50 py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30 disabled:opacity-55"
              />
            </div>
          </div>

          {errorMsg && (
            <div className="flex items-start gap-2 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-400">
              <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
          {infoMsg && (
            <div className="flex items-start gap-2 rounded-lg border border-blue-500/40 bg-blue-500/10 px-3 py-2 text-xs text-blue-400">
              <span>ℹ️ {infoMsg}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="group flex w-full items-center justify-center gap-2 rounded-xl brand-gradient py-2.5 text-sm font-semibold text-white shadow-[0_8px_30px_-12px_var(--color-primary)] transition-all hover:brightness-105 active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <span>{isSignUp ? "Sign Up" : "Sign In"}</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </>
            )}
          </button>
        </form>

        {/* Separator */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border/80" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-[#1E293B] px-2 text-muted-foreground rounded">Or continue with</span>
          </div>
        </div>

        {/* Google OAuth Button */}
        <button
          type="button"
          disabled={loading}
          onClick={handleGoogleSignIn}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-border bg-background/40 py-2.5 text-sm font-semibold text-foreground hover:bg-accent/60 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24">
            <path fill="#EA4335" d="M12 5.04c1.67 0 3.2.58 4.38 1.71l3.27-3.27C17.67 1.63 15.02 1 12 1 7.37 1 3.4 3.65 1.5 7.5l3.88 3c.9-2.73 3.45-4.46 6.62-4.46z"/>
            <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.34H12v4.44h6.44c-.28 1.47-1.11 2.72-2.36 3.56l3.66 2.84c2.14-1.97 3.75-4.87 3.75-8.5z"/>
            <path fill="#FBBC05" d="M5.38 10.5c-.23-.68-.36-1.42-.36-2.18s.13-1.5.36-2.18L1.5 3.14C.54 5.07 0 7.22 0 9.5s.54 4.43 1.5 6.36l3.88-3z"/>
            <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.66-2.84c-1.02.68-2.33 1.09-4.3 1.09-3.17 0-5.72-1.73-6.62-4.46L1.5 16.88C3.4 20.73 7.37 23 12 23z"/>
          </svg>
          <span>Google</span>
        </button>

        {/* Toggle Mode */}
        <div className="mt-6 text-center text-xs">
          <span className="text-muted-foreground">
            {isSignUp ? "Already have an account? " : "New to Wikipedia Research? "}
          </span>
          <button
            type="button"
            disabled={loading}
            onClick={() => { setIsSignUp(!isSignUp); setErrorMsg(""); setInfoMsg(""); }}
            className="font-semibold text-primary hover:underline"
          >
            {isSignUp ? "Sign in instead" : "Create an account"}
          </button>
        </div>
      </div>
    </div>
  );
}
