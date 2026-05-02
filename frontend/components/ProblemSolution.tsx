"use client";

import { WarningCircle, Clock, TrendUp, Database, Brain, ChartLine } from "@phosphor-icons/react";

export default function ProblemSolution() {
  return (
    <>
      {/* ── Problem Section ─────────────────────────────────── */}
      <section className="bg-background overflow-hidden border-t border-line/40">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-10 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
            
            {/* Text Content */}
            <div className="max-w-xl">
              <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
                Software Cost Estimation Is Still Guesswork
              </h2>
              <p className="mt-6 text-lg leading-8 text-muted">
                Teams rely on assumptions, spreadsheets, and inconsistent methods — leading to missed deadlines and budget overruns.
              </p>
              
              <div className="mt-12 space-y-6">
                {/* Card 1 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:rotate-[1.5deg] hover:bg-red-50 hover:border-red-200">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-muted/10 text-muted transition-colors group-hover:bg-red-100 group-hover:text-red-600">
                    <WarningCircle size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-red-900">Unreliable Estimates</h3>
                    <p className="mt-1 text-sm text-muted">Manual estimates vary wildly across teams and projects.</p>
                  </div>
                </div>
                
                {/* Card 2 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:-rotate-[1deg] hover:bg-red-50 hover:border-red-200">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-muted/10 text-muted transition-colors group-hover:bg-red-100 group-hover:text-red-600">
                    <Clock size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-red-900">Missed Deadlines</h3>
                    <p className="mt-1 text-sm text-muted">Inaccurate planning leads to delays and scope creep.</p>
                  </div>
                </div>

                {/* Card 3 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:rotate-[1deg] hover:bg-red-50 hover:border-red-200">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-muted/10 text-muted transition-colors group-hover:bg-red-100 group-hover:text-red-600">
                    <TrendUp size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-red-900">Budget Overruns</h3>
                    <p className="mt-1 text-sm text-muted">Small miscalculations scale into major financial risks.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Visual (Chaotic) */}
            <div className="relative h-[450px] sm:h-[500px] w-full rounded-3xl flex items-center justify-center overflow-visible">
               
               {/* Downward Trend Chart */}
               <div className="absolute top-[5%] right-[15%] w-40 h-32 bg-white rounded-xl border border-line shadow-md rotate-[18deg] p-4 animate-float opacity-70">
                  <div className="flex items-end h-full gap-2 opacity-60">
                     <div className="w-1/4 bg-red-400 h-full rounded-t-sm"></div>
                     <div className="w-1/4 bg-red-400 h-3/4 rounded-t-sm"></div>
                     <div className="w-1/4 bg-red-400 h-1/2 rounded-t-sm"></div>
                     <div className="w-1/4 bg-red-400 h-1/4 rounded-t-sm"></div>
                  </div>
               </div>

               {/* Distorted Spreadsheet */}
               <div className="absolute top-[15%] left-[5%] sm:left-4 w-56 sm:w-64 h-32 bg-white rounded-xl border border-line shadow-lg rotate-[-12deg] p-4 animate-float delay-100 opacity-90 hover:rotate-[-8deg] transition-all">
                  <div className="h-4 w-1/2 bg-muted/20 rounded mb-4"></div>
                  <div className="space-y-2">
                    <div className="h-2 w-full bg-[#e87070]/30 rounded"></div>
                    <div className="h-2 w-3/4 bg-[#e87070]/30 rounded"></div>
                    <div className="h-2 w-5/6 bg-[#e87070]/30 rounded"></div>
                  </div>
               </div>
               
               {/* Jagged Line Graph */}
               <div className="absolute top-[40%] right-[2%] sm:right-8 w-48 sm:w-56 h-40 bg-white rounded-xl border border-line shadow-lg rotate-[8deg] p-4 animate-float delay-300 opacity-90 hover:rotate-[12deg] transition-all">
                  <div className="h-full w-full border-b-2 border-l-2 border-muted/20 relative">
                     <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
                       <polyline points="0,90 20,70 50,85 80,40 110,60 140,20" fill="none" stroke="#d45b5b" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                     </svg>
                  </div>
               </div>

               {/* Broken Pie Chart */}
               <div className="absolute bottom-[20%] right-[15%] w-24 h-24 bg-white rounded-full border border-line shadow-md rotate-[-25deg] p-2 animate-float delay-400 opacity-60">
                  <div className="w-full h-full rounded-full border-[6px] border-dashed border-red-300"></div>
                  <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-red-400 rounded-tr-full origin-bottom-left rotate-[25deg] translate-x-3 translate-y-2 shadow-sm"></div>
               </div>

               {/* Total Cost Alert */}
               <div className="absolute bottom-[10%] left-[10%] sm:left-1/4 w-60 sm:w-72 h-20 bg-white rounded-xl border border-line shadow-lg rotate-[-5deg] p-4 flex items-center justify-between animate-float delay-200 opacity-90 hover:rotate-0 transition-all z-10">
                  <span className="text-sm font-mono text-muted/80">Projected Cost</span>
                  <span className="text-xl font-mono text-red-500 font-bold blur-[1px]">$2??,???</span>
               </div>
            </div>

          </div>
        </div>
      </section>

      {/* ── Solution Section ─────────────────────────────────── */}
      <section className="bg-white overflow-hidden border-t border-line/40 relative">
        {/* Soft glow background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-[20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-primary/[0.04] blur-3xl" />
        </div>

        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-10 lg:py-32 relative">
          <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
            
            {/* Visual (Clean/Structured) */}
            <div className="order-2 lg:order-1 relative h-[450px] sm:h-[500px] w-full rounded-3xl flex items-center justify-center overflow-visible">
               
               {/* Clean Dashboard Elements */}
               <div className="absolute top-[10%] left-[5%] sm:left-12 w-56 sm:w-64 h-32 bg-white rounded-xl border border-primary/10 shadow-[0_8px_30px_rgba(44,76,59,0.08)] p-5 transition-transform hover:scale-105 duration-500 hover:shadow-[0_12px_40px_rgba(44,76,59,0.12)]">
                  <div className="flex justify-between items-center mb-5">
                    <div className="h-4 w-1/3 bg-primary/20 rounded-md"></div>
                    <div className="h-4 w-4 bg-primary/20 rounded-full"></div>
                  </div>
                  <div className="space-y-3">
                    <div className="h-2 w-full bg-primary/10 rounded-md"></div>
                    <div className="h-2 w-full bg-primary/10 rounded-md"></div>
                    <div className="h-2 w-2/3 bg-primary/10 rounded-md"></div>
                  </div>
               </div>
               
               <div className="absolute top-[35%] right-[2%] sm:right-10 w-48 sm:w-60 h-40 bg-white rounded-xl border border-primary/10 shadow-[0_8px_30px_rgba(44,76,59,0.08)] p-5 transition-transform hover:scale-105 duration-500 hover:shadow-[0_12px_40px_rgba(44,76,59,0.12)]">
                  <div className="h-full w-full flex items-end justify-between gap-1.5 sm:gap-2">
                     <div className="w-full bg-primary/20 rounded-t-md h-[30%]"></div>
                     <div className="w-full bg-primary/40 rounded-t-md h-[55%]"></div>
                     <div className="w-full bg-primary/70 rounded-t-md h-[80%]"></div>
                     <div className="w-full bg-primary rounded-t-md h-[100%] relative">
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-primary">Accurate</div>
                     </div>
                  </div>
               </div>

               {/* Confidence Score Donut */}
               <div className="absolute top-[5%] right-[25%] sm:right-1/4 w-28 h-28 bg-white rounded-full border border-primary/10 shadow-[0_8px_30px_rgba(44,76,59,0.08)] flex items-center justify-center transition-transform hover:scale-105 duration-500 hover:shadow-[0_12px_40px_rgba(44,76,59,0.12)]">
                  <div className="relative w-20 h-20 rounded-full border-4 border-primary/10">
                     <div className="absolute inset-0 rounded-full border-4 border-primary border-r-transparent border-b-transparent rotate-45"></div>
                     <div className="absolute inset-0 flex items-center justify-center flex-col">
                        <span className="text-lg font-bold text-primary leading-none">94%</span>
                        <span className="text-[8px] text-muted font-bold uppercase tracking-widest mt-1">Conf</span>
                     </div>
                  </div>
               </div>

               {/* Smooth Trend Line */}
               <div className="absolute bottom-[25%] right-[10%] sm:right-[15%] w-40 h-24 bg-white rounded-xl border border-primary/10 shadow-[0_8px_30px_rgba(44,76,59,0.08)] p-4 transition-transform hover:scale-105 duration-500 hover:shadow-[0_12px_40px_rgba(44,76,59,0.12)]">
                  <div className="h-full w-full relative">
                     <svg className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
                       <path d="M0,40 C20,40 30,10 50,20 C70,30 90,5 110,0" fill="none" stroke="rgb(44 76 59)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                     </svg>
                     <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full border-2 border-white"></div>
                  </div>
               </div>

               <div className="absolute bottom-[10%] left-[10%] sm:left-[20%] w-60 sm:w-72 h-24 bg-white rounded-xl border border-primary/10 shadow-[0_8px_30px_rgba(44,76,59,0.08)] p-5 flex items-center justify-between transition-transform hover:scale-105 duration-500 hover:shadow-[0_12px_40px_rgba(44,76,59,0.12)] z-10">
                  <div>
                    <span className="block text-[11px] uppercase tracking-widest text-muted font-bold">Predicted Effort</span>
                    <span className="block mt-1 text-2xl font-serif text-primary">12.4 Months</span>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <ChartLine size={24} weight="bold" />
                  </div>
               </div>
            </div>

            {/* Text Content */}
            <div className="order-1 lg:order-2 max-w-xl">
              <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
                Replace Guesswork with Data-Driven Estimation
              </h2>
              <p className="mt-6 text-lg leading-8 text-muted">
                SoftEstimate uses real project data and machine learning to deliver fast, consistent, and accurate cost predictions.
              </p>
              
              <div className="mt-12 space-y-6">
                {/* Block 1 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:shadow-[0_8px_30px_rgba(44,76,59,0.08)] hover:-translate-y-1 hover:bg-primary/5 hover:border-primary/20">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                    <Database size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-primary">Powered by Real Data</h3>
                    <p className="mt-1 text-sm text-muted">Built on industry datasets like COCOMO and NASA projects.</p>
                  </div>
                </div>
                
                {/* Block 2 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:shadow-[0_8px_30px_rgba(44,76,59,0.08)] hover:-translate-y-1 hover:bg-primary/5 hover:border-primary/20">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                    <Brain size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-primary">Intelligent Predictions</h3>
                    <p className="mt-1 text-sm text-muted">Advanced models analyze patterns to estimate effort accurately.</p>
                  </div>
                </div>

                {/* Block 3 */}
                <div className="group flex gap-5 rounded-2xl bg-card p-6 shadow-sm border border-line/40 transition-all duration-300 hover:shadow-[0_8px_30px_rgba(44,76,59,0.08)] hover:-translate-y-1 hover:bg-primary/5 hover:border-primary/20">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                    <ChartLine size={24} weight="duotone" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg transition-colors group-hover:text-primary">Instant Results</h3>
                    <p className="mt-1 text-sm text-muted">Get reliable estimates in seconds with minimal input.</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>
    </>
  );
}
