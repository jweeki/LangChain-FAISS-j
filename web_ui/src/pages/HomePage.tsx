import { Link } from "react-router-dom";
import { SiteHeader } from "../components/SiteHeader";
import "../styles/home.css";

const HERO_TAGS = [
  "\u6301\u7eed\u6269\u5c55\u4e2d",
];

export function HomePage() {
  return (
    <main className="site-shell">
      <SiteHeader rightSlot={<Link to="/console">{"\u5411\u91cf\u68c0\u7d22\u63a7\u5236\u53f0"}</Link>} />

      <section className="hero hero-single reveal reveal-2">
        <div className="hero-copy">
          <p className="eyebrow">Jweeki Virtual Blog Site</p>
          <h1>{"Jweeki\u865a\u62df\u6570\u5b57\u57fa\u7ad9"}</h1>
          <p className="hero-text">
            {
              "\u8fd9\u662f\u4e00\u4e2a\u9762\u5411\u957f\u671f\u5efa\u8bbe\u7684\u6570\u5b57\u57fa\u7ad9\uff0c\u540e\u7eed\u5c06\u9010\u6b65\u5b66\u4e60\u642d\u5efa\u4e2a\u4eba\u535a\u5ba2\u3001\u865a\u62df\u8d27\u5e01\u4ea4\u6613\u7ad9\u70b9\u3001\u9ad8\u7aef\u7f8e\u5de5\u8bbe\u8ba1\u9875\u9762\uff0c\u5b9e\u73b0\u591a\u573a\u666f\u3001\u591a\u7ef4\u5ea6\u7684\u6280\u672f\u4e0e\u8bbe\u8ba1\u5b9e\u8df5\u63a2\u7d22\u3002"
            }
          </p>

          <div className="hero-actions">
            <Link className="secondary-link" to="/console">
              {"\u8fdb\u5165\u5411\u91cf\u63a7\u5236\u53f0"}
            </Link>
          </div>

          <div className="hero-tags">
            {HERO_TAGS.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
