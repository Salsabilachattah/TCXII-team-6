import Link from "next/dist/client/link";
import Image from "next/image";
import { Oswald, BBH_Bogle } from "next/font/google";

const oswald = Oswald({ subsets: ["latin"], weight: ["200", "700"] });
const bbhBogle = BBH_Bogle({ subsets: ["latin"], weight: "400" });
const Signin = () => {
    return (
      <main className="flex flex-col items-center pt-2 min-h-screen bg-cover bg-center bg-[url('../public/background-tc.jpg')]">
      <div className="mt-8 rounded flex items-center justify-center">
        <Image width={200} height={200} alt="doxa logo" src="/doxalogo.svg" />
      </div>
      <div className="mask-type:luminance">
        <h1 className={`text-4xl font-bold bbh-bogle-regular bg-gradient-to-r from-black via-blue-900 to-blue-800 bg-clip-text text-transparent`}>Welcome Back</h1>

<p className="text-gray-400 text-sm mt-2 leading-relaxed">
  Sign in to continue to your dashboard.
</p>
        <div className="flex flex-col ">
          <input placeholder="Email" className="bg-blue-700/31 text-white p-3 rounded-lg mb-4"/>
          <input placeholder="Password" className="bg-blue-700/31 text-black p-3 rounded-lg mb-4"/>
        </div>
      </div>
    </main>
    );
} 
export default Signin;