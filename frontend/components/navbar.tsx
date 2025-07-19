import Image from "next/image";

export default function Navbar() {
  return (
    <div
      className="navbar flex justify-between p-4 border-b top-0 left-0 w-full z-50 bg-[#F5F9FF]"
      style={{
        borderBottomColor: "#3A86FF",
        position: "fixed",
        width: "100%",
        paddingBottom: "0px",
      }}
    >
      <div className="logo-icon-and-search flex items-center gap-4">
        <Image src="/logo.jpg" alt="Logo" width={105} height={65} />
      </div>
      <div className="links flex gap-20">
        <a
          href="/"
          className="hover:scale-110 transition-transform duration-300 ease-in-out relative group"
        >
          <Image src="/home.png" alt="home" width={35} height={35} />
          <span className="absolute left-1/2 -translate-x-1/2 top-10 bg-[#3A86FF] text-white text-xs rounded-2xl px-3 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shadow">
            Home
          </span>
        </a>
        <a
          href="/reels"
          className="hover:scale-110 transition-transform duration-300 ease-in-out relative group"
        >
          <Image src="/reels.png" alt="reels" width={35} height={35} />
          <span className="absolute left-1/2 -translate-x-1/2 top-10 bg-[#3A86FF] text-white text-xs rounded-2xl px-3 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shadow">
            Reels
          </span>
        </a>
        <a
          href="/challenge"
          className="hover:scale-110 transition-transform duration-300 ease-in-out relative group"
        >
          <Image src="/challenge.png" alt="challenge" width={35} height={35} />
          <span className="absolute left-1/2 -translate-x-1/2 top-10 bg-[#3A86FF] text-white text-xs rounded-2xl px-3 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shadow">
            Challenge
          </span>
        </a>
        <a
          href="/organize"
          className="hover:scale-110 transition-transform duration-300 ease-in-out relative group"
        >
          <Image src="/organize.png" alt="organize" width={35} height={35} />
          <span className="absolute left-1/2 -translate-x-1/2 top-10 bg-[#3A86FF] text-white text-xs rounded-2xl px-3 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shadow">
            Organize
          </span>
        </a>
        <a
          href="/school"
          className="hover:scale-110 transition-transform duration-300 ease-in-out relative group"
        >
          <Image src="/school.png" alt="school" width={40} height={40} />
          <span className="absolute left-1/2 -translate-x-1/2 top-10 bg-[#3A86FF] text-white text-xs rounded-2xl px-3 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shadow">
            School
          </span>
        </a>
      </div>
      <div className="right-links flex">
        <a
          href="/user-profile"
          className="hover:scale-110 transition-transform duration-300 ease-in-out"
        >
          <Image
            src="/user-profile.png"
            alt="user-profile"
            width={45}
            height={45}
          />
        </a>
      </div>
    </div>
  );
}
