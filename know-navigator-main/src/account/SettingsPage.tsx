import { Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/services/supabase";
import { toast } from "sonner";
import { ArrowLeft, User, Mail, FileText, Loader2, LogOut, Save } from "lucide-react";
import type { User as SupabaseUser } from "@supabase/supabase-js";

export function SettingsPage() {
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form states
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        navigate({ to: "/" });
      } else {
        setUser(session.user);
        setFullName(session.user.user_metadata?.full_name || "");
        setUsername(session.user.user_metadata?.username || "");
        setBio(session.user.user_metadata?.bio || "");
      }
      setLoading(false);
    });
  }, [navigate]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (saving) return;

    setSaving(true);
    const toastId = toast.loading("Saving changes...");

    try {
      const { error } = await supabase.auth.updateUser({
        data: {
          full_name: fullName,
          username: username,
          bio: bio,
        },
      });

      if (error) throw error;
      toast.success("Profile updated successfully!", { id: toastId });
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to update profile.", { id: toastId });
    } finally {
      setSaving(false);
    }
  };

  const handleSignOut = async () => {
    const toastId = toast.loading("Signing out...");
    try {
      await supabase.auth.signOut();
      toast.success("Signed out successfully!", { id: toastId });
      navigate({ to: "/" });
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to sign out.", { id: toastId });
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-background px-4 py-8">
      {/* Background aurora */}
      <div className="aurora pointer-events-none absolute inset-0 opacity-60" />

      <div className="relative z-10 w-full max-w-lg overflow-hidden rounded-2xl border border-border/80 bg-surface/40 p-6 sm:p-8 glass-strong shadow-elegant">
        {/* Navigation header */}
        <div className="flex items-center gap-3 mb-6">
          <Link
            to="/"
            className="grid h-9 w-9 place-items-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            aria-label="Back to research workspace"
            title="Back to workspace"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-foreground">Account Settings</h1>
            <p className="text-xs text-muted-foreground">Manage your research profile credentials</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSave} className="space-y-5">
          {/* Email (Read Only) */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Email Address (Login ID)
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground/60" />
              <input
                type="text"
                disabled
                value={user?.email || ""}
                className="w-full cursor-not-allowed rounded-lg border border-border bg-background/20 py-2.5 pl-10 pr-3 text-sm text-muted-foreground opacity-60 focus:outline-none"
              />
            </div>
          </div>

          {/* Full Name */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Full Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Researcher"
                disabled={saving}
                className="w-full rounded-lg border border-border bg-background/50 py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30 disabled:opacity-50"
              />
            </div>
          </div>

          {/* Username */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Username
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 text-sm text-muted-foreground -translate-y-1/2 font-semibold">@</span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="jane_res"
                disabled={saving}
                className="w-full rounded-lg border border-border bg-background/50 py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30 disabled:opacity-50"
              />
            </div>
          </div>

          {/* Bio */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Bio / Research Field
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Briefly describe your field of study or research interest..."
                disabled={saving}
                rows={3}
                className="w-full rounded-lg border border-border bg-background/50 py-2.5 pl-10 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30 disabled:opacity-50 resize-none"
              />
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-3">
            <button
              type="submit"
              disabled={saving}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl brand-gradient py-2.5 text-sm font-semibold text-white shadow-[0_8px_30px_-12px_var(--color-primary)] transition-all hover:brightness-105 active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleSignOut}
              disabled={saving}
              className="flex items-center justify-center gap-2 rounded-xl border border-border bg-background/40 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-accent/60 hover:text-destructive transition-colors disabled:opacity-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
