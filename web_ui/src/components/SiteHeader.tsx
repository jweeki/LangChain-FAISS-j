import type { ReactNode } from "react";

type SiteHeaderProps = {
  rightSlot: ReactNode;
};

export function SiteHeader({ rightSlot }: SiteHeaderProps) {
  return (
    <header className="topbar glass reveal reveal-1">
      <div className="brand-lockup">
        <span className="brand-dot" />
        <div>
          <p className="brand-kicker">Jweeki Digital Presence - wangjie</p>
          <strong>{"Jweeki Virtual Blog Site"}</strong>
        </div>
      </div>
      <nav className="topnav">{rightSlot}</nav>
    </header>
  );
}
