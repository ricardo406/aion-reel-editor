import { Composition, staticFile } from "remotion";
import { AionEdit } from "./AionEdit";
import editData from "./edit.json";

const FPS = editData.fps ?? 30;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="AionEdit"
      component={AionEdit}
      durationInFrames={editData.durationInFrames}
      fps={FPS}
      width={editData.width ?? 1080}
      height={editData.height ?? 1920}
      defaultProps={{ src: staticFile(editData.source) }}
    />
  );
};
