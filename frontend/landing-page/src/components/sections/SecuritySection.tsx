import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { ShieldCheck, Server, CloudOff, Lock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function SecuritySection() {
  const { t } = useTranslation();

  const features = [
    {
      icon: <Server className="w-8 h-8 text-primary" />,
      titleKey: "security.features.local_llm",
      descKey: "security.usp_text"
    },
    {
      icon: <CloudOff className="w-8 h-8 text-rose-500" />,
      titleKey: "security.features.no_cloud",
      descKey: "security.usp_text"
    },
    {
      icon: <ShieldCheck className="w-8 h-8 text-emerald-500" />,
      titleKey: "security.features.audit",
      descKey: "security.usp_text"
    }
  ];

  return (
    <section id="security" className="py-20 bg-accent/30 px-6 flex items-center justify-center flex-col border-y border-border">
      <div className="max-w-5xl w-full">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-500 text-xs font-bold uppercase tracking-wider mb-4">
            <Lock className="w-3.5 h-3.5" />
            <span>Security Pillar</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            {t("security.title")}
          </h2>
          <p className="text-xl font-mono italic font-semibold text-primary max-w-2xl mx-auto mb-6 bg-primary/5 py-3 px-6 rounded-lg border border-dashed border-primary/30 inline-block">
            "{t("security.subtitle")}"
          </p>
          <p className="text-muted-foreground max-w-xl mx-auto">
            {t("security.usp_text")}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: idx * 0.15 }}
            >
              <Card className="h-full border-border bg-card hover:border-primary/50 transition-all duration-300 group hover:shadow-lg hover:-translate-y-1">
                <CardHeader className="pb-2 flex items-center md:items-start">
                  <div className="p-3 rounded-xl bg-accent group-hover:bg-primary/10 transition-colors mb-4">
                    {feat.icon}
                  </div>
                  <CardTitle className="text-xl font-semibold leading-snug text-center md:text-left w-full">
                    {t(feat.titleKey)}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-2 text-muted-foreground text-sm leading-relaxed text-center md:text-left">
                  {t(feat.descKey).slice(0, 85)}...
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
