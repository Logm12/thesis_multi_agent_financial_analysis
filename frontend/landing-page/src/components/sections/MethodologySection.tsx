import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { FileCheck, BarChart3, CheckCircle2, Layers } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

export function MethodologySection() {
  const { t } = useTranslation();

  return (
    <section id="methodology" className="py-20 px-6 bg-background flex items-center justify-center flex-col">
      <div className="max-w-5xl w-full space-y-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-500 text-xs font-bold uppercase tracking-wider mb-4">
            <Layers className="w-3.5 h-3.5" />
            <span>Methodology</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            {t("methodology.title")}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            {t("methodology.subtitle")}
          </p>
        </motion.div>

        {/* Grid for Progress Score & Accordion steps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          
          {/* Left: RAGAS Score Matrix */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, y: 0, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <Card className="border-border shadow-sm hover:shadow-md transition-shadow duration-300 h-full">
              <CardHeader className="border-b bg-accent/20 pb-4">
                <CardTitle className="flex items-center gap-3 text-xl font-bold">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  RAGAS Evaluation Matrix
                </CardTitle>
                <CardDescription>
                  Standardized quantitative metrics from automated evaluation workflows.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8 space-y-8">
                {/* Metric 1 */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm font-semibold">
                    <span className="text-foreground">{t("methodology.faithfulness")}</span>
                    <span className="text-indigo-600 font-mono bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-400 dark:border-indigo-800">
                      0.95 / 1.0
                    </span>
                  </div>
                  <Progress value={95} className="h-3.5 bg-muted [&>div]:bg-primary" />
                  <p className="text-xs text-muted-foreground italic">
                    * Measures if the answer is solely generated from facts found in retrieved PDF chunks.
                  </p>
                </div>

                {/* Metric 2 */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm font-semibold">
                    <span className="text-foreground">{t("methodology.relevancy")}</span>
                    <span className="text-indigo-600 font-mono bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-400 dark:border-indigo-800">
                      0.92 / 1.0
                    </span>
                  </div>
                  <Progress value={92} className="h-3.5 bg-muted [&>div]:bg-indigo-500/70" />
                  <p className="text-xs text-muted-foreground italic">
                    * Ensures the generated output directly resolves the explicit financial question.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Right: Accordion Execution Sequence */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, y: 0, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="space-y-6">
              <h3 className="text-2xl font-bold tracking-tight flex items-center gap-3 mb-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                {t("methodology.agent_steps.title")}
              </h3>
              
              <Accordion className="w-full border border-border rounded-xl overflow-hidden bg-card">
                <AccordionItem value="step1" className="border-b last:border-b-0">
                  <AccordionTrigger className="px-6 hover:bg-accent/50 font-semibold text-left">
                    {t("methodology.agent_steps.step1_title")}
                  </AccordionTrigger>
                  <AccordionContent className="px-6 text-muted-foreground leading-relaxed pb-4">
                    {t("methodology.agent_steps.step1_desc")}
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="step2" className="border-b last:border-b-0">
                  <AccordionTrigger className="px-6 hover:bg-accent/50 font-semibold text-left">
                    {t("methodology.agent_steps.step2_title")}
                  </AccordionTrigger>
                  <AccordionContent className="px-6 text-muted-foreground leading-relaxed pb-4">
                    {t("methodology.agent_steps.step2_desc")}
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="step3" className="border-b last:border-b-0">
                  <AccordionTrigger className="px-6 hover:bg-accent/50 font-semibold text-left">
                    {t("methodology.agent_steps.step3_title")}
                  </AccordionTrigger>
                  <AccordionContent className="px-6 text-muted-foreground leading-relaxed pb-4">
                    {t("methodology.agent_steps.step3_desc")}
                  </AccordionContent>
                </AccordionItem>
                <AccordionItem value="step4" className="border-b last:border-b-0">
                  <AccordionTrigger className="px-6 hover:bg-accent/50 font-semibold text-left">
                    {t("methodology.agent_steps.step4_title")}
                  </AccordionTrigger>
                  <AccordionContent className="px-6 text-muted-foreground leading-relaxed pb-4">
                    {t("methodology.agent_steps.step4_desc")}
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </motion.div>
        </div>

        {/* Case Studies Tabs UI */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="pt-8 w-full"
        >
          <Card className="border-border shadow-sm bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl font-bold flex items-center justify-center gap-3">
                <FileCheck className="w-6 h-6 text-primary" />
                {t("methodology.case_studies.title")}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <Tabs defaultValue="retail" className="w-full flex flex-col items-center">
                <TabsList className="w-full max-w-lg grid grid-cols-3 h-11 mb-8">
                  <TabsTrigger value="retail" className="font-semibold text-sm">{t("methodology.case_studies.retail")}</TabsTrigger>
                  <TabsTrigger value="banking" className="font-semibold text-sm">{t("methodology.case_studies.banking")}</TabsTrigger>
                  <TabsTrigger value="tech" className="font-semibold text-sm">{t("methodology.case_studies.tech")}</TabsTrigger>
                </TabsList>
                
                <TabsContent value="retail" className="w-full text-center space-y-4 p-6 bg-accent/20 border border-dashed border-border rounded-xl focus:outline-none">
                  <h4 className="text-xl font-bold text-primary">{t("methodology.case_studies.retail")}</h4>
                  <p className="text-muted-foreground leading-relaxed max-w-2xl mx-auto font-medium">
                    {t("methodology.case_studies.retail_desc")}
                  </p>
                </TabsContent>
                
                <TabsContent value="banking" className="w-full text-center space-y-4 p-6 bg-accent/20 border border-dashed border-border rounded-xl focus:outline-none">
                  <h4 className="text-xl font-bold text-primary">{t("methodology.case_studies.banking")}</h4>
                  <p className="text-muted-foreground leading-relaxed max-w-2xl mx-auto font-medium">
                    {t("methodology.case_studies.banking_desc")}
                  </p>
                </TabsContent>
                
                <TabsContent value="tech" className="w-full text-center space-y-4 p-6 bg-accent/20 border border-dashed border-border rounded-xl focus:outline-none">
                  <h4 className="text-xl font-bold text-primary">{t("methodology.case_studies.tech")}</h4>
                  <p className="text-muted-foreground leading-relaxed max-w-2xl mx-auto font-medium">
                    {t("methodology.case_studies.tech_desc")}
                  </p>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}
