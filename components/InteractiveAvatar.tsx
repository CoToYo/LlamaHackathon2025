import {
  AvatarQuality,
  StreamingEvents,
  VoiceChatTransport,
  VoiceEmotion,
  StartAvatarRequest,
  STTProvider,
  ElevenLabsModel,
  TaskType,
  TaskMode,
} from "@heygen/streaming-avatar";
import { useEffect, useRef, useState } from "react";
import { useMemoizedFn, useUnmount } from "ahooks";
import { fetchComments, formatCommentForSpeech } from "@/app/lib/commentsApi";

import { Button } from "./Button";
import { AvatarConfig } from "./AvatarConfig";
import { AvatarVideo } from "./AvatarSession/AvatarVideo";
import { useStreamingAvatarSession } from "./logic/useStreamingAvatarSession";
import { AvatarControls } from "./AvatarSession/AvatarControls";
import { useVoiceChat } from "./logic/useVoiceChat";
import { StreamingAvatarProvider, StreamingAvatarSessionState } from "./logic";
import { LoadingIcon } from "./Icons";
import { MessageHistory } from "./AvatarSession/MessageHistory";

import { AVATARS } from "@/app/lib/constants";

import LlamaAPIClient from 'llama-api-client';

type Message = {
  role: "user" | "assistant" | "system";
  content: string;
};

const DEFAULT_CONFIG: StartAvatarRequest = {
  quality: AvatarQuality.Low,
  avatarName: AVATARS[0].avatar_id,
  knowledgeId: undefined,
  voice: {
    rate: 1.5,
    emotion: VoiceEmotion.EXCITED,
    model: ElevenLabsModel.eleven_flash_v2_5,
  },
  language: "en",
  voiceChatTransport: VoiceChatTransport.WEBSOCKET,
  sttSettings: {
    provider: STTProvider.DEEPGRAM,
  },
};

function InteractiveAvatar() {
  const { initAvatar, startAvatar, stopAvatar, sessionState, stream } =
    useStreamingAvatarSession();
  const { startVoiceChat } = useVoiceChat();

  const [config, setConfig] = useState<StartAvatarRequest>(DEFAULT_CONFIG);
  const mediaStream = useRef<HTMLVideoElement>(null);

  async function fetchAccessToken() {
    try {
      const response = await fetch("/api/get-access-token", {
        method: "POST",
      });
      const token = await response.text();

      console.log("Access Token:", token); // Log the token to verify

      return token;
    } catch (error) {
      console.error("Error fetching access token:", error);
      throw error;
    }
  }

  const readPitchScript = async () => {
    try {
      const response = await fetch('/api/get-script');
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      return data.chunks;
    } catch (error) {
      console.error('Error reading pitch script:', error);
      return null;
    }
  };

  const processCommentsAsChunks = async (avatar: any) => {
    const comments = await fetchComments();

    if (comments.length === 0) {
      return [];
    }

    const commentChunks = [];

    // Add introduction for comments
    commentChunks.push("Let me address some questions from our viewers.");

    for (const comment of comments) {
      try {
        const apiResponse = await fetch("/api/llama-chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [
              {
                role: "system",
                content: `You are a great live stream host. You are engaging and friendly. 
                You will receive audience's comments and our response to the comment. Rephrase them into a short and concise response.`
              },
              {
                role: "user",
                content: formatCommentForSpeech(comment),
              },
            ],
          }),
        });

        if (!apiResponse.ok) {
          console.error("Failed to call Llama API");
          continue;
        }

        const result = await apiResponse.json();
        commentChunks.push(result.content);
      } catch (error) {
        console.error("Error processing comment:", error);
      }
    }

    // Add closing for comments
    if (commentChunks.length > 1) { // More than just the introduction
      commentChunks.push("Thank you for your questions! Now let's continue with our presentation.");
    }

    return commentChunks;
  };

  const speakChunksSequentially = async (avatar: any, chunks: string[]) => {
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];

      // Speak the current chunk
      await avatar.speak({
        text: chunk,
        taskType: TaskType.REPEAT,
        taskMode: TaskMode.SYNC,
      });

      // After each chunk, check for new comments and process them
      const commentChunks = await processCommentsAsChunks(avatar);

      if (commentChunks.length > 0) {
        // Insert comment chunks into the sequence after the current chunk
        const remainingChunks = chunks.slice(i + 1);
        chunks.splice(i + 1, 0, ...commentChunks);

        // Update the loop to include the new chunks
        // We don't need to increment i here because we're inserting chunks
        // and the loop will naturally process them
      }
    }
  };

  const getScriptChunks = async (script: string) => {
    // Feed pitch script to llama and get script chunks back
    // The script chunks are the parts of the script that are separated by a new line
  };

  const startSessionV2 = useMemoizedFn(async (isVoiceChat: boolean) => {
    try {
      const newToken = await fetchAccessToken();
      const avatar = initAvatar(newToken);

      avatar.on(StreamingEvents.AVATAR_START_TALKING, (e) => {
        console.log("Avatar started talking", e);
      });
      avatar.on(StreamingEvents.AVATAR_STOP_TALKING, (e) => {
        console.log("Avatar stopped talking", e);
      });
      avatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {
        console.log("Stream disconnected");
      });
      avatar.on(StreamingEvents.STREAM_READY, (event) => {
        console.log(">>>>> Stream ready:", event.detail);
      });
      avatar.on(StreamingEvents.USER_START, (event) => {
        console.log(">>>>> User started talking:", event);
      });
      avatar.on(StreamingEvents.USER_STOP, (event) => {
        console.log(">>>>> User stopped talking:", event);
      });
      avatar.on(StreamingEvents.USER_END_MESSAGE, (event) => {
        console.log(">>>>> User end message:", event);
      });
      avatar.on(StreamingEvents.USER_TALKING_MESSAGE, (event) => {
        console.log(">>>>> User talking message:", event);
      });
      avatar.on(StreamingEvents.AVATAR_TALKING_MESSAGE, (event) => {
        console.log(">>>>> Avatar talking message:", event);
      });
      avatar.on(StreamingEvents.AVATAR_END_MESSAGE, (event) => {
        console.log(">>>>> Avatar end message:", event);
      });

      await startAvatar(config);

      if (isVoiceChat) {
        await startVoiceChat();
      }

      avatar.speak({
        text: "Welcome to the live stream hosted by Lisa, we are very excited to welcome you",
        taskType: TaskType.REPEAT,
        taskMode: TaskMode.SYNC,
      }).then(() => {
        return avatar.speak({
          text: "Let's get started",
          taskType: TaskType.REPEAT,
          taskMode: TaskMode.SYNC,
        });
      }).then(async () => {
        const scriptChunks = await readPitchScript();
        if (scriptChunks && scriptChunks.length > 0) {
          await speakChunksSequentially(avatar, scriptChunks);
        }
      }).catch((error) => {
        console.error('Error in greeting sequence:', error);
      });

    } catch (error) {
      console.error("Error starting avatar session:", error);
    }
  });

  useUnmount(() => {
    stopAvatar();
  });

  useEffect(() => {
    if (stream && mediaStream.current) {
      mediaStream.current.srcObject = stream;
      mediaStream.current.onloadedmetadata = () => {
        mediaStream.current!.play();
      };
    }
  }, [mediaStream, stream]);

  return (
    <div className="w-full flex flex-col gap-4">
      <div className="flex flex-col rounded-xl bg-zinc-900 overflow-hidden">
        <div className="relative w-full aspect-video overflow-hidden flex flex-col items-center justify-center">
          {sessionState !== StreamingAvatarSessionState.INACTIVE ? (
            <AvatarVideo ref={mediaStream} />
          ) : (
            <AvatarConfig config={config} onConfigChange={setConfig} />
          )}
        </div>
        <div className="flex flex-col gap-3 items-center justify-center p-4 border-t border-zinc-700 w-full">
          {sessionState === StreamingAvatarSessionState.CONNECTED ? (
            <AvatarControls />
          ) : sessionState === StreamingAvatarSessionState.INACTIVE ? (
            <div className="flex flex-row gap-4">
              <Button onClick={() => startSessionV2(true)}>
                Start Voice Chat
              </Button>
              <Button onClick={() => startSessionV2(false)}>
                Start Text Chat
              </Button>
            </div>
          ) : (
            <LoadingIcon />
          )}
        </div>
      </div>
      {sessionState === StreamingAvatarSessionState.CONNECTED && (
        <MessageHistory />
      )}
    </div>
  );
}

export default function InteractiveAvatarWrapper() {
  return (
    <StreamingAvatarProvider basePath={process.env.NEXT_PUBLIC_BASE_API_URL}>
      <InteractiveAvatar />
    </StreamingAvatarProvider>
  );
}
