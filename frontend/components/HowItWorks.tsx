"use client";

import { Database, Sliders, ChartLine } from "@phosphor-icons/react";

export default function HowItWorks() {
  return (
    <section className="bg-[#f3efe6] py-24 lg:py-32 overflow-hidden border-y border-line/40 relative">
      <div className="mx-auto max-w-6xl px-6 lg:px-10">
        
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-20 animate-fade-in-up">
          <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
            From Idea to Estimate in Seconds
          </h2>
          <p className="mt-4 text-lg leading-8 text-muted">
            A simple, guided process designed for fast and accurate cost estimation.
          </p>
        </div>

        {/* Steps Container */}
        <div className="relative grid md:grid-cols-3 gap-8 md:gap-12">
          
          {/* Connecting Line (Desktop only) */}
          <div className="hidden md:block absolute top-[128px] left-[15%] right-[15%] h-[2px] bg-line/60 z-0">
             {/* The line connecting the top cards visually */}
          </div>

          {/* STEP 1 */}
          <div className="group relative z-10 flex flex-col items-center animate-fade-in-up delay-100">
            {/* Visual */}
            <div className="w-full h-64 bg-white rounded-3xl border border-line/50 shadow-sm flex items-center justify-center relative overflow-hidden transition-all duration-500 group-hover:shadow-[0_12px_40px_rgba(44,76,59,0.08)] group-hover:-translate-y-2 group-hover:border-primary/20">
               {/* Decorative background */}
               <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] to-transparent"></div>
               
               {/* 3D Floating Cards */}
               <div className="relative w-full h-full flex items-center justify-center">
                  <div className="absolute left-[15%] w-24 h-32 bg-white rounded-lg border border-line shadow-md rotate-[-12deg] p-3 transition-transform duration-500 group-hover:-rotate-[-16deg] group-hover:scale-105 opacity-80">
                    <div className="w-6 h-6 rounded bg-muted/10 mb-3"></div>
                    <div className="h-2 w-full bg-muted/20 rounded mb-1.5"></div>
                    <div className="h-2 w-2/3 bg-muted/20 rounded"></div>
                  </div>
                  
                  <div className="absolute z-10 w-28 h-36 bg-white rounded-xl border-2 border-primary/20 shadow-lg p-3 transition-transform duration-500 group-hover:scale-110">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-3">
                      <Database size={16} weight="fill" />
                    </div>
                    <div className="h-2.5 w-full bg-primary/20 rounded mb-2"></div>
                    <div className="h-2 w-3/4 bg-primary/10 rounded"></div>
                  </div>

                  <div className="absolute right-[15%] w-24 h-32 bg-white rounded-lg border border-line shadow-md rotate-[12deg] p-3 transition-transform duration-500 group-hover:rotate-[16deg] group-hover:scale-105 opacity-80">
                    <div className="w-6 h-6 rounded bg-muted/10 mb-3"></div>
                    <div className="h-2 w-full bg-muted/20 rounded mb-1.5"></div>
                    <div className="h-2 w-2/3 bg-muted/20 rounded"></div>
                  </div>
               </div>
            </div>

            {/* Content */}
            <div className="mt-8 text-center px-2">
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm mb-4 transition-colors group-hover:bg-primary group-hover:text-white">
                01
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2 transition-colors group-hover:text-primary">Select Your Project Type</h3>
              <p className="text-sm text-muted">Choose the type of software you want to build.</p>
            </div>
          </div>

          {/* STEP 2 */}
          <div className="group relative z-10 flex flex-col items-center animate-fade-in-up delay-200">
            {/* Visual */}
            <div className="w-full h-64 bg-white rounded-3xl border border-line/50 shadow-sm flex items-center justify-center relative overflow-hidden transition-all duration-500 group-hover:shadow-[0_12px_40px_rgba(44,76,59,0.08)] group-hover:-translate-y-2 group-hover:border-primary/20">
               <div className="absolute inset-0 bg-gradient-to-b from-transparent to-primary/[0.02]"></div>
               
               {/* Sliders UI */}
               <div className="w-48 bg-white rounded-xl border border-line/60 shadow-lg p-5 z-10 transition-transform duration-500 group-hover:scale-105">
                 
                 <div className="space-y-4">
                   <div>
                     <div className="flex justify-between mb-1.5">
                       <div className="h-1.5 w-12 bg-muted/30 rounded"></div>
                       <div className="h-1.5 w-6 bg-primary/30 rounded transition-all duration-700 group-hover:bg-primary/60"></div>
                     </div>
                     <div className="relative h-1.5 w-full bg-muted/10 rounded-full">
                       <div className="absolute top-0 left-0 h-full w-[70%] bg-primary rounded-full transition-all duration-700 group-hover:w-[85%]"></div>
                       <div className="absolute top-1/2 -translate-y-1/2 left-[70%] -translate-x-1/2 w-3 h-3 bg-white border-2 border-primary rounded-full shadow-sm transition-all duration-700 group-hover:left-[85%]"></div>
                     </div>
                   </div>
                   
                   <div>
                     <div className="flex justify-between mb-1.5">
                       <div className="h-1.5 w-16 bg-muted/30 rounded"></div>
                       <div className="h-1.5 w-6 bg-primary/30 rounded transition-all duration-700 group-hover:bg-primary/60"></div>
                     </div>
                     <div className="relative h-1.5 w-full bg-muted/10 rounded-full">
                       <div className="absolute top-0 left-0 h-full w-[40%] bg-primary rounded-full transition-all duration-700 group-hover:w-[55%]"></div>
                       <div className="absolute top-1/2 -translate-y-1/2 left-[40%] -translate-x-1/2 w-3 h-3 bg-white border-2 border-primary rounded-full shadow-sm transition-all duration-700 group-hover:left-[55%]"></div>
                     </div>
                   </div>

                   <div>
                     <div className="flex justify-between mb-1.5">
                       <div className="h-1.5 w-10 bg-muted/30 rounded"></div>
                       <div className="h-1.5 w-6 bg-primary/30 rounded transition-all duration-700 group-hover:bg-primary/60"></div>
                     </div>
                     <div className="relative h-1.5 w-full bg-muted/10 rounded-full">
                       <div className="absolute top-0 left-0 h-full w-[85%] bg-primary rounded-full transition-all duration-700 group-hover:w-[60%]"></div>
                       <div className="absolute top-1/2 -translate-y-1/2 left-[85%] -translate-x-1/2 w-3 h-3 bg-white border-2 border-primary rounded-full shadow-sm transition-all duration-700 group-hover:left-[60%]"></div>
                     </div>
                   </div>
                 </div>

               </div>
            </div>

            {/* Content */}
            <div className="mt-8 text-center px-2">
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm mb-4 transition-colors group-hover:bg-primary group-hover:text-white">
                02
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2 transition-colors group-hover:text-primary">Enter Key Details</h3>
              <p className="text-sm text-muted">Provide a few simple inputs about your project.</p>
            </div>
          </div>

          {/* STEP 3 */}
          <div className="group relative z-10 flex flex-col items-center animate-fade-in-up delay-300">
            {/* Visual */}
            <div className="w-full h-64 bg-white rounded-3xl border border-line/50 shadow-sm flex items-center justify-center relative overflow-hidden transition-all duration-500 group-hover:shadow-[0_12px_40px_rgba(44,76,59,0.08)] group-hover:-translate-y-2 group-hover:border-primary/20">
               <div className="absolute inset-0 bg-primary/[0.02]"></div>
               <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-primary/5 rounded-full blur-2xl transition-all duration-500 group-hover:bg-primary/10"></div>
               
               {/* Result Card */}
               <div className="w-52 bg-white rounded-xl border border-primary/20 shadow-lg p-5 z-10 text-center transition-transform duration-500 group-hover:scale-110">
                 <div className="mx-auto w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-4 transition-transform duration-500 group-hover:scale-110 group-hover:bg-primary group-hover:text-white">
                    <ChartLine size={20} weight="bold" />
                 </div>
                 <div className="text-[10px] uppercase tracking-widest text-muted font-bold mb-1">Total Effort</div>
                 <div className="text-3xl font-serif text-primary mb-3">12.4<span className="text-sm font-sans text-muted">mo</span></div>
                 
                 <div className="h-1 w-full bg-line/50 rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-[0%] rounded-full transition-all duration-1000 group-hover:w-[100%]"></div>
                 </div>
                 <div className="mt-2 text-[9px] text-muted font-medium transition-colors duration-500 group-hover:text-primary">HIGH CONFIDENCE</div>
               </div>
            </div>

            {/* Content */}
            <div className="mt-8 text-center px-2">
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white font-bold text-sm mb-4 shadow-md transition-transform duration-500 group-hover:scale-110">
                03
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2 transition-colors group-hover:text-primary">Get Instant Estimate</h3>
              <p className="text-sm text-muted">Receive your cost and effort prediction instantly.</p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
