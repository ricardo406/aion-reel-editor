import React from "react";
import {
  AbsoluteFill,
  Easing,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Captions } from "./Captions";
import editData from "./edit.json";

type Segment = {
  fromFrame: number;
  durationInFrames: number;
  trimBefore: number;
};

type Broll = { startFrame: number; durationInFrames: number; src: string };

// Full-screen 9:16 B-roll clip (same size/framing as the reference reels).
// Covers the talking head; the voice continues underneath (clip is muted).
// Quick fade reads as a cut; subtle push-in adds life. Captions stay on top.
const BrollClip: React.FC<{ b: Broll }> = ({ b }) => {
  const local = useCurrentFrame();
  const FADE = 3;
  const d = b.durationInFrames;
  const opacity = interpolate(
    local,
    [0, FADE, d - FADE, d],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const scale = interpolate(local, [0, d], [1.0, 1.05], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ transform: `scale(${scale})`, overflow: "hidden" }}>
        <OffthreadVideo
          src={b.src}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// frames where giant keywords hit -> sync a small viral punch on the video
const EMPHASIS_STARTS = (editData.captionPages as any[])
  .filter((p) => p.emphasis)
  .map((p) => p.startFrame as number);

const SegmentVideo: React.FC<{ seg: Segment; src: string; index: number }> = ({
  seg,
  src,
  index,
}) => {
  const local = useCurrentFrame(); // 0..durationInFrames (local to this Sequence)
  const global = seg.fromFrame + local;

  // Alternate framing scale per cut so each jump reads as an intentional
  // punch-in/out (hides the talking-head position jump). Even=wider, odd=tighter.
  const base = index % 2 === 0 ? 1.04 : 1.10;
  const slow = interpolate(local, [0, seg.durationInFrames], [base, base + 0.04], {
    extrapolateRight: "clamp",
  });
  // quick snap on the cut (start of segment)
  const cutSnap = interpolate(local, [0, 8], [0.06, 0], {
    extrapolateRight: "clamp",
  });
  // viral hook zoom: only on the opening segment. Hard punch-in slam to grab
  // attention in the first frames, snappy ease-out settle = energetic open.
  const hookSlam =
    index === 0
      ? interpolate(global, [0, 8, 34], [0.24, 0.11, 0], {
          easing: Easing.out(Easing.cubic),
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;
  // second viral punch a beat later (on the opening phrase) so the hook keeps
  // moving and "connects" before the first giant keyword lands.
  const hookPunch =
    index === 0
      ? interpolate(global, [18, 26, 40], [0, 0.09, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;
  const hookZoom = hookSlam + hookPunch;
  // punch synced to giant keyword beats (boosted for more viral pop)
  let beat = 0;
  for (const s of EMPHASIS_STARTS) {
    const d = global - s;
    if (d >= 0 && d < 9) {
      beat = Math.max(beat, interpolate(d, [0, 9], [0.12, 0]));
    }
  }
  const scale = slow + cutSnap + hookZoom + beat;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${scale})` }}>
        <OffthreadVideo
          src={src}
          trimBefore={seg.trimBefore}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const AionEdit: React.FC<{ src: string }> = ({ src }) => {
  const segments = editData.segments as Segment[];
  const broll = ((editData as any).broll ?? []) as Broll[];
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {segments.map((seg, i) => (
        <Sequence
          key={i}
          from={seg.fromFrame}
          durationInFrames={seg.durationInFrames}
        >
          <SegmentVideo seg={seg} src={src} index={i} />
        </Sequence>
      ))}

      {/* Full-screen B-roll layer: above the talking head, below the captions */}
      {broll.map((b, i) => (
        <Sequence
          key={`broll-${i}`}
          from={b.startFrame}
          durationInFrames={b.durationInFrames}
        >
          <BrollClip b={{ ...b, src: staticFile(b.src) }} />
        </Sequence>
      ))}

      <Captions />
    </AbsoluteFill>
  );
};
