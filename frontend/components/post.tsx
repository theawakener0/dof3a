"use client";
import "../app/globals.css";
import Image from "next/image";
import { useState } from "react";

type PostProps = {
  posterName: string;
  posterPfp: string;
  content: string;
  postImage?: string;
  userName: string; // current user
};

type ReactionType = "like" | "love" | "laugh" | null;

type Comment = {
  name: string;
  text: string;
};

export default function Post({
  posterName,
  posterPfp,
  content,
  postImage,
  userName,
}: PostProps) {
  const [reactions, setReactions] = useState<{
    [K in ReactionType as Exclude<K, null>]: string[];
  }>({
    like: [],
    love: [],
    laugh: [],
  });
  const [userReaction, setUserReaction] = useState<ReactionType>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentInput, setCommentInput] = useState("");
  const [showComments, setShowComments] = useState(false);
  const [showReactionMenu, setShowReactionMenu] = useState(false);
  const [showReactPopup, setShowReactPopup] = useState(false);

  // Add postDate state and update it every minute
  const [postDate, setPostDate] = useState<Date>(new Date());

  // Optional: Update postDate every minute (for demo, not for real posts)
  // useEffect(() => {
  //   const interval = setInterval(() => setPostDate(new Date()), 60000);
  //   return () => clearInterval(interval);
  // }, []);

  // Format date for display
  const formatDate = (date?: Date) => {
    if (!date) return "Just now";
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "Just now";
    if (diffMin < 60) return `${diffMin} min ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr} hr ago`;
    return date.toLocaleDateString();
  };

  // Helper to get total reacts
  const totalReacts = Object.values(reactions).reduce(
    (acc, arr) => acc + arr.length,
    0
  );

  // Helper to get all users who reacted
  const getReactors = () => {
    const result: { type: ReactionType; users: string[] }[] = [];
    for (const type of ["like", "love", "laugh"] as ReactionType[]) {
      result.push({
        type,
        users: reactions[type as Exclude<ReactionType, null>],
      });
    }
    return result;
  };

  // Smooth and easy to change react, undo if clicking same
  const handleReaction = (type: ReactionType) => {
    if (!type) return;
    let updated = { ...reactions };
    if (userReaction === type) {
      // Undo reaction
      updated[type] = updated[type].filter((name) => name !== userName);
      setUserReaction(null);
    } else {
      // Remove previous reaction
      if (userReaction && updated[userReaction]) {
        updated[userReaction] = updated[userReaction].filter(
          (name) => name !== userName
        );
      }
      // Add new reaction
      updated[type] = [...updated[type], userName];
      setUserReaction(type);
    }
    setReactions(updated);
    setShowReactionMenu(false);
  };

  // Undo react if clicking the react button when already reacted
  const handleReactButtonClick = () => {
    if (userReaction) {
      handleReaction(userReaction);
    } else {
      setShowReactionMenu(true);
    }
  };

  const handleCommentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (commentInput.trim()) {
      setComments([...comments, { name: userName, text: commentInput }]);
      setCommentInput("");
    }
  };

  // Only one popup at a time
  const handleShowReactPopup = () => {
    setShowReactPopup((prev) => !prev);
    setShowComments(false);
  };
  const handleShowComments = () => {
    setShowComments((prev) => !prev);
    setShowReactPopup(false);
  };

  // Prevent reaction menu from moving away when hovering between button and menu
  let reactionMenuTimeout: NodeJS.Timeout | null = null;
  const handleReactionMenuEnter = () => {
    if (reactionMenuTimeout) clearTimeout(reactionMenuTimeout);
    setShowReactionMenu(true);
  };
  const handleReactionMenuLeave = () => {
    reactionMenuTimeout = setTimeout(() => setShowReactionMenu(false), 120);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-xl mx-auto my-8 border border-gray-200 font-sans relative">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 pt-4 pb-2">
        <Image
          src={posterPfp}
          alt={posterName}
          width={48}
          height={48}
          className="rounded-full border border-gray-300"
        />
        <div>
          <span className="font-semibold text-gray-900">{posterName}</span>
          <div className="text-xs text-gray-500">{formatDate(postDate)}</div>
        </div>
      </div>
      {/* Content */}
      <div className="px-4 pb-2">
        <p className="mb-2 text-[1.15rem]">{content}</p>
        {postImage && (
          <div className="rounded-lg overflow-hidden border border-gray-100 mb-2">
            <Image
              src={postImage}
              alt="Post"
              width={500}
              height={300}
              className="w-full object-cover"
            />
          </div>
        )}
        {/* Reacts and Comments Count */}
        <div className="flex gap-6 justify-start mb-2 px-2 text-gray-600 font-medium">
          <button
            className="hover:underline transition-all duration-300"
            onClick={handleShowReactPopup}
          >
            {totalReacts} Reacts
          </button>
          <button
            className="hover:underline transition-all duration-300"
            onClick={handleShowComments}
          >
            {comments.length} Comments
          </button>
        </div>
        {/* Reacts Popup */}
        <div className="relative">
          <div
            className={`transition-all duration-300 ${
              showReactPopup
                ? "opacity-100 scale-100 pointer-events-auto"
                : "opacity-0 scale-95 pointer-events-none"
            } absolute bg-white border rounded-lg shadow-lg px-4 py-3 z-20 mt-2 w-64`}
            style={{ left: 0 }}
          >
            <div className="font-semibold mb-2">Reactions</div>
            {getReactors().map(({ type, users }) => (
              <div key={type} className="flex items-center gap-2 mb-1">
                <span>
                  {type === "like" && "👍"}
                  {type === "love" && "❤️"}
                  {type === "laugh" && "😂"}
                </span>
                <span className="font-medium">{users.length}</span>
                <span className="text-xs text-gray-500">
                  {users.length > 0 ? users.join(", ") : ""}
                </span>
              </div>
            ))}
          </div>
        </div>
        {/* Enhanced Buttons */}
        <div className="flex gap-4 mt-2 w-[98%] mx-auto">
          <div
            className="relative flex-1"
            onMouseEnter={handleReactionMenuEnter}
            onMouseLeave={handleReactionMenuLeave}
          >
            {/* Reaction Options Above Button */}
            <div
              className={`transition-all duration-300 absolute left-1/2 -translate-x-1/2 -top-12 flex gap-2 bg-white border rounded-lg shadow-lg px-3 py-2 z-10 ${
                showReactionMenu
                  ? "opacity-100 scale-100 pointer-events-auto"
                  : "opacity-0 scale-95 pointer-events-none"
              }`}
              onMouseEnter={handleReactionMenuEnter}
              onMouseLeave={handleReactionMenuLeave}
            >
              <button
                className="hover:scale-110 transition-transform duration-300 ease-in-out"
                onClick={() => handleReaction("like")}
                aria-label="Like"
                type="button"
              >
                👍
              </button>
              <button
                className="hover:scale-110 transition-transform duration-300 ease-in-out"
                onClick={() => handleReaction("love")}
                aria-label="Love"
                type="button"
              >
                ❤️
              </button>
              <button
                className="hover:scale-110 transition-transform duration-300 ease-in-out"
                onClick={() => handleReaction("laugh")}
                aria-label="Laugh"
                type="button"
              >
                😂
              </button>
            </div>
            <button
              className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-full shadow transition-all duration-300 ease-in-out
                ${
                  userReaction === "like"
                    ? "bg-blue-100 text-blue-600"
                    : userReaction === "love"
                    ? "bg-pink-100 text-pink-600"
                    : userReaction === "laugh"
                    ? "bg-yellow-100 text-yellow-600"
                    : "bg-gray-100 text-gray-700"
                }
              `}
              type="button"
              onClick={handleReactButtonClick}
            >
              {!userReaction && "❤️"}
              {userReaction === "like" && "👍"}
              {userReaction === "love" && "❤️"}
              {userReaction === "laugh" && "😂"}
            </button>
          </div>
          <div className="flex-1">
            <button
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-full shadow bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-600 transition-all duration-300 ease-in-out"
              onClick={handleShowComments}
              type="button"
            >
              💬
            </button>
          </div>
        </div>
      </div>
      {/* Divider */}
      <div className="border-t border-gray-100 my-2"></div>
      {/* Comments Section */}
      <div
        className={`transition-all duration-300 ${
          showComments
            ? "opacity-100 scale-100 pointer-events-auto"
            : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        {showComments && (
          <div className="px-4 pb-4">
            <form onSubmit={handleCommentSubmit} className="flex gap-2 mb-3">
              <input
                type="text"
                value={commentInput}
                onChange={(e) => setCommentInput(e.target.value)}
                placeholder="Write a comment..."
                className="border rounded-full px-4 py-2 flex-1 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600"
              >
                Post
              </button>
            </form>
            <div>
              {comments.length === 0 ? (
                <p className="text-gray-500 text-sm">No comments yet.</p>
              ) : (
                <ul className="space-y-2">
                  {comments.map((comment, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Image
                        src="/user-profile.png"
                        alt="User"
                        width={32}
                        height={32}
                        className="rounded-full border border-gray-200"
                      />
                      <div className="bg-gray-100 rounded-lg px-3 py-2">
                        <span className="font-semibold text-gray-800">
                          {comment.name}
                        </span>
                        <div className="text-gray-700 text-sm">
                          {comment.text}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
