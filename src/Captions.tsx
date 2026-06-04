import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont as loadJakarta } from "@remotion/google-fonts/PlusJakartaSans";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import editData from "./edit.json";

const { fontFamily: JAKARTA } = loadJakarta("normal", { weights: ["700", "800"] });
const { fontFamily: PLAYFAIR } = loadPlayfair("italic", { weights: ["700"] });

/**
 * AION HYBRID captions v4.
 * - Base: clean sans (Inter), sentence case, SMALLER, ultra-subtle elegant shadow.
 * - Karaoke-lite: active word lifts slightly.
 * - GIANT keywords: Playfair Display ITALIC (luxury serif), Title-case, distinct + high-end.
 * - No colors. Face stays clean.
 */

type Word = { text: string; startFrame: number; endFrame: number };
type Page = { startFrame: number; endFrame: number; emphasis?: boolean; words: Word[] };

const SANS = `${JAKARTA}, "Helvetica Neue", "Segoe UI", system-ui, sans-serif`;
const SERIF = `${PLAYFAIR}, "Georgia", serif`;

// elegant soft HALO (reference style): even dark glow all around + slight depth,
// no hard stroke. Lifts the white off any background gracefully.
const SOFT_SHADOW =
  "0 0 12px rgba(0,0,0,0.55), 0 0 22px rgba(0,0,0,0.32), 0 2px 5px rgba(0,0,0,0.55)";
const SOFT_SHADOW_GIANT =
  "0 0 18px rgba(0,0,0,0.55), 0 0 34px rgba(0,0,0,0.34), 0 3px 8px rgba(0,0,0,0.55)";

const stripPunct = (t: string) => t.replace(/[.,;:!?]+$/g, "");
const titleCase = (t: string) =>
  t.charAt(0).toUpperCase() + t.slice(1).toLowerCase();

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pages = (editData.captionPages ?? []) as Page[];

  const page = pages.find((p) => frame >= p.startFrame && frame < p.endFrame);
  if (!page) return null;

  // ---------- GIANT emphasis (luxury serif italic) ----------
  if (page.emphasis) {
    const pop = spring({
      frame: frame - page.startFrame,
      fps,
      config: { damping: 13, mass: 0.6, stiffness: 120 },
      durationInFrames: 16,
    });
    const scale = interpolate(pop, [0, 1], [0.6, 1]);
    const opacity = interpolate(frame - page.startFrame, [0, 5], [0, 1], {
      extrapolateRight: "clamp",
    });
    const raw = stripPunct(page.words[0].text);
    const text = /^\d+$/.test(raw) ? raw : titleCase(raw);
    return (
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "48%",
          display: "flex",
          justifyContent: "center",
          padding: "0 60px",
        }}
      >
        <div
          style={{
            transform: `scale(${scale})`,
            opacity,
            fontFamily: SERIF,
            fontStyle: "italic",
            fontWeight: 700,
            fontSize: 128,
            lineHeight: 1,
            letterSpacing: "-0.01em",
            color: "#FFFFFF",
            textAlign: "center",
            textShadow: SOFT_SHADOW_GIANT,
          }}
        >
          {text}
        </div>
      </div>
    );
  }

  // ---------- Normal phrase block: reference style ----------
  // Uniform solid white, STATIC (no karaoke, no scale drift), quick fade only.
  const enterOpacity = interpolate(frame - page.startFrame, [0, 3], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: "55%",
        display: "flex",
        justifyContent: "center",
        padding: "0 90px",
      }}
    >
      <div
        style={{
          opacity: enterOpacity,
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 50,
          lineHeight: 1.12,
          letterSpacing: "-0.01em",
          color: "#FFFFFF",
          textAlign: "center",
          maxWidth: 880,
          textShadow: SOFT_SHADOW,
        }}
      >
        {page.words.map((w) => w.text).join(" ")}
      </div>
    </div>
  );
};
