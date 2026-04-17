export function StructuralDiagram() {
  return (
    <div
      aria-hidden="true"
      role="img"
      className="w-full max-w-[480px] mx-auto"
    >
      <svg
        viewBox="0 0 480 240"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-auto"
      >
        {/* Beam — horizontal line */}
        <line
          x1="60" y1="120" x2="420" y2="120"
          stroke="var(--brand-text)" strokeWidth="3" strokeLinecap="round"
        />

        {/* Left support — triangle pin */}
        <polygon
          points="60,120 45,148 75,148"
          stroke="var(--brand-text)" strokeWidth="2" fill="none"
        />
        <line x1="38" y1="152" x2="82" y2="152" stroke="var(--brand-text)" strokeWidth="2" />

        {/* Right support — roller (circle on triangle) */}
        <polygon
          points="420,120 405,148 435,148"
          stroke="var(--brand-text)" strokeWidth="2" fill="none"
        />
        <circle cx="420" cy="155" r="5" stroke="var(--brand-text)" strokeWidth="2" fill="none" />
        <line x1="398" y1="164" x2="442" y2="164" stroke="var(--brand-text)" strokeWidth="2" />

        {/* Distributed load arrows — full beam coverage */}
        {[60, 105, 150, 195, 240, 285, 330, 375, 420].map((x, i) => (
          <g key={i}>
            <line x1={x} y1="80" x2={x} y2="116" stroke="var(--brand-accent)" strokeWidth="1.5" />
            <polygon points={`${x},120 ${x - 4},110 ${x + 4},110`} fill="var(--brand-accent)" />
          </g>
        ))}
        {/* Load line across top */}
        <line x1="60" y1="80" x2="420" y2="80" stroke="var(--brand-accent)" strokeWidth="1.5" strokeDasharray="4 2" />

        {/* Moment diagram — parabolic arc (path drawn with CSS animation) */}
        {/* Parabola: M 60,120 Q 240,195 420,120 — bending below beam for positive moment */}
        <path
          d="M 60,120 Q 240,195 420,120"
          stroke="var(--brand-accent)" strokeWidth="2.5"
          fill="none" strokeLinecap="round"
          strokeDasharray="500"
          strokeDashoffset="500"
          style={{
            animation: 'drawBeamDiagram 1.2s ease-out 0.4s forwards',
          }}
        />

        {/* M(x) label */}
        <text
          x="245" y="210"
          fontSize="12" fill="var(--brand-muted)"
          textAnchor="middle" fontFamily="var(--font-sans)"
          opacity="0"
          style={{ animation: 'fadeInLabel 0.4s ease-out 1.4s forwards' }}
        >
          M(x)
        </text>
      </svg>

      <style>{`
        @keyframes drawBeamDiagram {
          to { stroke-dashoffset: 0; }
        }
        @keyframes fadeInLabel {
          to { opacity: 1; }
        }
      `}</style>
    </div>
  )
}
