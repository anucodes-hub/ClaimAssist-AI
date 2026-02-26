import { motion } from 'framer-motion';
import { ShieldCheck, Zap, Activity, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="bg-dark min-h-screen text-white overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-accent/10 blur-[120px] rounded-full" />
      
      <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto relative z-10">
        <div className="text-2xl font-bold flex items-center gap-2">
          <ShieldCheck className="text-accent" /> ClaimAssist<span className="text-accent text-3xl">.</span>
        </div>
        <Link to="/login" className="bg-white/5 hover:bg-white/10 px-6 py-2 rounded-full border border-white/10 transition">Sign In</Link>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32 text-center relative z-10">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="text-6xl md:text-8xl font-bold tracking-tighter mb-6"
        >
          Insurance claims, <br />
          <span className="text-gray-500">handled by </span> <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">AI Intelligence.</span>
        </motion.h1>
        
        <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-10">
          Instant document validation, fraud detection, and automated payouts. 
          The modern standard for insurance processing.
        </p>

        <div className="flex justify-center gap-4">
          <Link to="/register" className="bg-accent hover:bg-blue-600 px-8 py-4 rounded-full font-bold flex items-center gap-2 transition">
            Get Started <ArrowRight size={20} />
          </Link>
        </div>

        {/* Bento Grid Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-24">
          {[
            { icon: <Zap />, title: "Real-time OCR", desc: "Extract data from any document in seconds." },
            { icon: <ShieldCheck />, title: "Fraud Guard", desc: "Cross-checks dates and signatures automatically." },
            { icon: <Activity />, title: "Health Scoring", desc: "AI-driven confidence scores for every claim." }
          ].map((item, i) => (
            <div key={i} className="bg-surface p-8 rounded-3xl border border-border text-left hover:border-accent/50 transition cursor-default">
              <div className="text-accent mb-4">{item.icon}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-gray-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

/*import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      <h1 className="text-5xl font-bold text-blue-500 mb-6">
        ClaimAssist AI
      </h1>

      <p className="text-gray-400 max-w-xl text-center mb-8">
        AI-powered insurance claim verification using OCR, Computer Vision,
        and Predictive Analytics. Upload documents and receive real-time
        approval insights with Explainable AI.
      </p>

      <div className="flex gap-4">
        <Link
          to="/upload"
          className="bg-blue-600 px-6 py-3 rounded-lg hover:bg-blue-700 transition"
        >
          Submit Claim
        </Link>

        <Link
          to="/dashboard"
          className="border border-blue-600 px-6 py-3 rounded-lg hover:bg-blue-600 transition"
        >
          View Dashboard
        </Link>
      </div>
    </div>
  );
}
*/