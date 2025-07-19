import Post from "../components/post";
import Sidebar from "../components/sidebar";

export default function Home() {
  return (
    <div className="flex bg-[#F5F9FF] min-h-screen font-['Segoe_UI',Arial,sans-serif]">
      <Sidebar />
      {/* Main Content */}
      <main className="flex-1 px-4 py-8 ml-80">
        <Post
          posterName="Omar Ashraf"
          content="hello! I am omar , I am at grade 7"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="Aly Ahmed"
          content="hello! I am Aly , I am at grade 9"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="sayed youssef"
          content="hello! I am sayed"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="Ashraf ahmed"
          content="hello! I am Ashraf , I am at grade 11"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="Fady Nassar"
          content="hello! I am Fady "
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="ellewa"
          content="hello! I am omar , I am at grade 7"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
        <Post
          posterName="Omar Ashraf"
          content="hello! I am omar , I am at grade 7"
          userName="Ahmed Ashraf"
          posterPfp="/user-profile.png"
        />
      </main>
    </div>
  );
}
