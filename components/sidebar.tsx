import Image from "next/image";
import Link from "next/link";
import {
  CheckCircleIcon,
  PuzzlePieceIcon,
  AcademicCapIcon,
  BuildingLibraryIcon,
  UsersIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/solid";

export default function Sidebar() {
  return (
    <aside
      className="w-80 bg-white border-r-2 border-[#3A86FF] text-[#3A86FF] flex flex-col py-10 px-8 shadow-xl"
      style={{
        position: "fixed",
        left: 0,
        top: "81px",
        height: "100%",
      }}
    >
      <Link
        href="/profile"
        className="flex items-center gap-4 mb-10 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200"
      >
        <Image
          src="/user-profile.png"
          alt="Profile"
          width={48}
          height={48}
          className="rounded-full border-2 border-[#3A86FF]"
        />
        <span className="font-bold text-2xl text-black">Ahmed Ashraf</span>
      </Link>
      <button className="mb-10 px-5 py-3 rounded-2xl bg-[#3A86FF] text-white font-semibold hover:bg-[#245bbf] transition-colors duration-200 flex items-center gap-3 shadow">
        <ArrowRightOnRectangleIcon className="w-7 h-7" />
        Logout
      </button>
      <input
        type="text"
        placeholder="Search :Dof3a"
        className="mb-10 px-4 py-2 rounded-2xl border-2 border-[#3A86FF] focus:outline-none focus:ring-2 focus:ring-[#3A86FF] text-base bg-[#F5F9FF] text-[#495867] placeholder-[#3A86FF] transition-all duration-300 shadow"
      />
      <nav className="flex flex-col gap-10">
        <Link
          href="/todo-list"
          className="flex items-center gap-4 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200 text-xl"
        >
          <CheckCircleIcon className="w-7 h-7" />
          <span className="font-semibold text-black">To-Do List</span>
        </Link>
        <Link
          href="/games"
          className="flex items-center gap-4 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200 text-xl"
        >
          <PuzzlePieceIcon className="w-7 h-7" />
          <span className="font-semibold text-black">Games</span>
        </Link>
        <Link
          href="/school"
          className="flex items-center gap-4 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200 text-xl"
        >
          <AcademicCapIcon className="w-7 h-7" />
          <span className="font-semibold text-black">School</span>
        </Link>
        <Link
          href="/classroom"
          className="flex items-center gap-4 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200 text-xl"
        >
          <BuildingLibraryIcon className="w-7 h-7" />
          <span className="font-semibold text-black">Classroom</span>
        </Link>
        <Link
          href="/study-group"
          className="flex items-center gap-4 hover:bg-[#e3edff] rounded-2xl px-4 py-3 transition-colors duration-200 text-xl"
        >
          <UsersIcon className="w-7 h-7" />
          <span className="font-semibold text-black">Study Group</span>
        </Link>
      </nav>
    </aside>
  );
}
