"use client";
import Image from "next/image";
import Link from "next/link";

export default function register() {
  return (
    <main className="flex flex-col items-center pt-2 min-h-screen bg-cover bg-center bg-[url('../public/background-tc.jpg')]">
      <div className="mt-8 rounded flex items-center justify-center">
        <Image width={200} height={200} alt="doxa logo" src="/doxalogo.svg" />
      </div>
      <div className="mt-8">
        <label className="text-2xl text-blue-900 font-bold">
          Centralize your customer support
        </label>
      </div>
      <div className="flex flex-col items-center justify-center py-2 mb-15 border border-2 border-blue/10 transition:all duration-500 bg-white/50 py-10 px-10 rounded-[30px] rounded-[40px] mt-8">
        <h1 className="text-blue-900 font-bold font-sans text-xl">
          Register Your Account
        </h1>
        <div className="flex flex-row justify-center m-0">
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">
              First Name<span className="text-red-500">*</span>
            </label>
            <input
              required
              type="name"
              placeholder="Enter your first name"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-300"
            />
          </div>
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">
              Last Name<span className="text-red-500">*</span>
            </label>
            <input
              required
              type="text"
              placeholder="Enter your darkom name"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
        </div>
        <div className="flex flex-row justify-center m-0">
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">
              Profession<span className="text-red-500">*</span>
            </label>
            <input
              required
              type="text"
              placeholder="Enter your profession"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">
              Phone number<span className="text-red-500">*</span>
            </label>
            <input
              required
              type="number"
              placeholder="Enter your phone number"
              className="max p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
        </div>
        <div className="flex flex-row justify-center m-0">
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">gender*</label>
            <input
              required
              type="text"
              placeholder="Create a password"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
          <div className="flex flex-col m-2 justify-space-evenly">
            <label className="text-blue-900 pl-2">Date of Birth*</label>
            <input
              required
              type="date"
              placeholder="Enter your email"
              className="px-11 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
        </div>
        <div className="flex flex-row justify-center m-0">
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">Email*</label>
            <input
              required
              type="email"
              placeholder="Enter your email"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
          <div className="flex flex-col m-2">
            <label className="text-blue-900 pl-2">Password*</label>
            <input
              required
              type="password"
              placeholder="Create a password"
              className="p-3 text-black bg-white/50 placeholder-gray-300 placeholder:text-sm bg-#0F172A border-[1px] m-2 rounded-[8px] h-8 focus:border-blue-600"
            />
          </div>
        </div>
        <div className="m-2 flex align-left">
          <p className="text-red-500 text-xs ">* Required fields</p>
        </div>
        <div>
          <button className="bg-blue-900 text-white px-6 py-2 rounded-[15px] mt-4 hover:bg-blue-700 transition duration-300">
            Create Account
          </button>
          <button className="bg-gray-300 text-black px-6 py-2 rounded-[15px] mt-4 ml-4 hover:bg-gray-400 transition duration-300">
            Sign in with Google
          </button>
        </div>
        <div>
          <p className="text-gray-600 text-m p-5 font-sans">
            Already have an account ?{" "}
            <Link
              href="/Signin"
              className="underline text-gray-600 active:text-gray-900">
              sign in
            </Link>
          </p>
        </div>
      </div>
      <footer className="h-8 bg-black-400"></footer>
    </main>
  );
}


