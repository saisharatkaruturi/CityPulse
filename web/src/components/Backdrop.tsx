/** The living colour field behind every glass surface: five slow-drifting blurred orbs. Decorative only;
 *  still under prefers-reduced-motion (tokens.css). Place once per page, inside an `.aurora` root. */
export function Backdrop() {
  return (
    <div className="backdrop" aria-hidden="true">
      <span className="orb orb-1" />
      <span className="orb orb-2" />
      <span className="orb orb-3" />
      <span className="orb orb-4" />
      <span className="orb orb-5" />
    </div>
  );
}
