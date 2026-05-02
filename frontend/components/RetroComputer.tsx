"use client";

import "./retro-computer.css";

export default function RetroComputer() {
    return (
        <div className="retro-wrapper relative w-full h-full min-h-[400px]">
            <div className="scene mx-auto translate-x-6 lg:translate-x-12 scale-[0.75] sm:scale-[0.85] lg:scale-[0.95] origin-center" id="scene">
                <div className="computer-unit">
                    <div className="face front">
                        <div className="screen-inset">
                            <div className="crt">
                                <div className="crt-glow">
                                    <div className="crt-ui">
                                        <div className="sidebar">
                                            <div className="icon-list">
                                                <div><span className="icon-circle blue"></span> System</div>
                                                <div><span className="icon-circle orange"></span> Disk A</div>
                                                <div><span className="icon-circle"></span> Trash</div>
                                                <div><span className="icon-circle"></span> Write</div>
                                                <div><span className="icon-circle"></span> Think</div>
                                            </div>
                                        </div>
                                        <div className="main-area">
                                            <div className="os-label">SoftOS 1.0</div>
                                            <div className="window">
                                                <div className="window-header">
                                                    <span>Untitled.txt</span>
                                                    <span>[x]</span>
                                                </div>
                                                <div className="typing-container">
                                                    <span id="typewriter">Hello! What is the software cost? </span><span className="cursor"></span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="logo-badge"></div>
                        <div className="floppy-slot"></div>

                        <div className="sticker sticker-ball"></div>
                        <div className="sticker sticker-star"></div>
                        <div className="sticker sticker-text">MACHINE<br />INTELLIGENCE</div>

                        <div className="grill">
                            <div className="vent"></div><div className="vent"></div><div className="vent"></div><div className="vent"></div>
                            <div className="vent"></div><div className="vent"></div><div className="vent"></div><div className="vent"></div>
                        </div>
                    </div>
                    <div className="face back"></div>
                    <div className="face left"></div>
                    <div className="face right"></div>
                    <div className="face top"></div>
                    <div className="face bottom"></div>

                </div>
            </div>
        </div>
    );
}
