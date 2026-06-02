 
import { Button } from "@/components/ui/button";

import type { Workspace } from "@/App";

export default function AuthPage({
  tenantSlug,
  email,
  password,
  setTenantSlug,
  setEmail,
  setPassword,
  authLoading,
  authError,
  isAuthed,
  workspaces,
  workspaceId,
  onWorkspaceChange,
  onLogin,
  onRegister,
  onLogout,
}: {
  tenantSlug: string;
  email: string;
  password: string;
  setTenantSlug: (v: string) => void;
  setEmail: (v: string) => void;
  setPassword: (v: string) => void;
  authLoading: boolean;
  authError: string | null;
  isAuthed: boolean;
  workspaces: Workspace[];
  workspaceId?: string;
  onWorkspaceChange: (v?: string) => void;
  onLogin: () => void;
  onRegister: () => void;
  onLogout: () => void;
}) {
  return (
    <div className="rounded-2xl border border-paper/10 bg-paper/5 p-5">
      <h2 className="font-display text-lg">Account</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div>
          <label className="block text-xs text-paper/70">Tenant slug</label>
          <input value={tenantSlug} onChange={(e) => setTenantSlug(e.target.value)} className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2" />
        </div>
        <div>
          <label className="block text-xs text-paper/70">Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2" />
        </div>
        <div>
          <label className="block text-xs text-paper/70">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2" />
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        {!isAuthed ? (
          <>
            <Button variant="outline" onClick={onRegister} disabled={authLoading}>
              {authLoading ? "Creating..." : "Register"}
            </Button>
            <Button onClick={onLogin} disabled={authLoading}>
              {authLoading ? "Signing in..." : "Login"}
            </Button>
          </>
        ) : (
          <Button variant="outline" onClick={onLogout}>
            Logout
          </Button>
        )}
      </div>

      {authError ? <div className="mt-3 text-sm text-red-300">{authError}</div> : null}

      <div className="mt-4">
        <label className="block text-xs text-paper/70">Workspace</label>
        <select value={workspaceId || ""} onChange={(e) => onWorkspaceChange(e.target.value || undefined)} className="mt-2 rounded-md border border-paper/10 bg-ink/40 px-3 py-2">
          <option value="">Select workspace</option>
          {workspaces.map((ws) => (
            <option key={ws.id} value={ws.id}>
              {ws.name} ({ws.slug})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
