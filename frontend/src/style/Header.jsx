export default function Header() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50">
            {/* Glassmorphism bar */}
            <div className="mx-4 mt-4 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md shadow-lg shadow-black/30">
                <div className="flex items-center justify-between px-6 py-3">

                    {/* Logo / Brand */}
                    <div className="flex items-center gap-2">
                        {/* Icon mark */}
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 shadow-md">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="white"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="h-4 w-4"
                            >
                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                            </svg>
                        </div>
                        {/* Brand name */}
                        <span className="text-xl font-bold tracking-tight text-white">
                            Vector
                        </span>
                    </div>

                    {/* Nav links */}
                    <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-white/60">
                        <a href="#" className="hover:text-white transition-colors duration-200">Dashboard</a>
                        <a href="#" className="hover:text-white transition-colors duration-200">Test Runs</a>
                        <a href="#" className="hover:text-white transition-colors duration-200">Reports</a>
                        <a href="#" className="hover:text-white transition-colors duration-200">Schemas</a>
                    </nav>

                    {/* CTA button */}
                    <button className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:opacity-90 active:scale-95 transition-all duration-200">
                        Run Tests
                    </button>

                </div>
            </div>
        </header>
    );
}
