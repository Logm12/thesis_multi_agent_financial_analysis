import React, { useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { KeyRound, Mail, Lock, ArrowLeft, CheckCircle, BrainCircuit } from "lucide-react";
import { useAuth } from "../../lib/auth-context";

interface LoginSectionProps {
  onBack: () => void;
  onSuccess: () => void;
}

export function LoginSection({ onBack, onSuccess }: LoginSectionProps) {
  const { t } = useTranslation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;

    setIsLoading(true);
    // Giả lập delay API đăng nhập 1.5s
    setTimeout(() => {
      login(email);
      setIsLoading(false);
      setIsSuccess(true);
      // Chuyển hướng sau thành công 1s
      setTimeout(() => {
        onSuccess();
      }, 1000);
    }, 1500);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 py-12 bg-gradient-to-br from-background via-accent/10 to-indigo-500/5">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="max-w-md w-full bg-card rounded-3xl border border-border shadow-2xl p-8 relative overflow-hidden"
      >
        {/* Back button */}
        <button 
          onClick={onBack}
          className="absolute left-6 top-6 text-muted-foreground hover:text-primary flex items-center gap-2 text-xs font-semibold tracking-wide uppercase transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {t("auth.btn_back")}
        </button>

        <div className="mt-8 text-center mb-8">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-500 mb-4">
            <BrainCircuit className="h-6 w-6 animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{t("auth.login_title")}</h2>
          <p className="text-xs text-muted-foreground mt-2 max-w-xs mx-auto leading-relaxed">
            {t("auth.login_subtitle")}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 relative">
          {/* Email Input */}
          <div className="space-y-2">
            <label className="text-xs font-bold tracking-wider uppercase text-muted-foreground px-1">{t("auth.username")}</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="email"
                required
                placeholder="admin@lumo.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-12 bg-accent/10 border-2 border-border rounded-xl pl-11 pr-4 text-sm focus:border-primary focus:outline-none outline-none transition-all duration-300"
              />
            </div>
          </div>

          {/* Password Input */}
          <div className="space-y-2">
            <label className="text-xs font-bold tracking-wider uppercase text-muted-foreground px-1">{t("auth.password")}</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-12 bg-accent/10 border-2 border-border rounded-xl pl-11 pr-4 text-sm focus:border-primary focus:outline-none outline-none transition-all duration-300"
              />
            </div>
          </div>

          <div className="flex items-center justify-between px-1 text-xs">
            <label className="flex items-center gap-2 cursor-pointer select-none text-muted-foreground hover:text-foreground">
              <input type="checkbox" className="rounded border-border text-primary focus:ring-primary" />
              <span>Ghi nhớ đăng nhập</span>
            </label>
            <a href="#" className="text-primary font-semibold hover:underline">Quên mật khẩu?</a>
          </div>

          {/* Submit button with active state transitions */}
          <button
            type="submit"
            disabled={isLoading || isSuccess}
            className="w-full h-12 mt-4 bg-primary text-primary-foreground rounded-xl font-bold shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 transition-all hover:opacity-95 hover:scale-[1.01] active:scale-100 disabled:opacity-70 disabled:scale-100 disabled:shadow-none overflow-hidden"
          >
            {isLoading ? (
              <>
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                >
                  <KeyRound className="w-5 h-5" />
                </motion.div>
                <span>Verifying access...</span>
              </>
            ) : isSuccess ? (
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center gap-2 text-emerald-400 font-extrabold"
              >
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                <span>Access Granted!</span>
              </motion.div>
            ) : (
              <>
                <KeyRound className="w-4 h-4" />
                <span>{t("auth.btn_login")}</span>
              </>
            )}
          </button>
        </form>

        <div className="text-center mt-8 text-xs text-muted-foreground border-t border-border pt-6 font-medium">
          Chưa có tài khoản? <a href="#" className="text-primary font-bold hover:underline">Đăng ký ngay</a>
        </div>
      </motion.div>
    </div>
  );
}
