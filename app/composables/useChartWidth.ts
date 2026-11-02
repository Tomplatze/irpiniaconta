import type { Ref } from 'vue';

/** Keep SVG labels in readable CSS-sized coordinates as a chart's container resizes. */
export function useChartWidth(element: Ref<HTMLElement | null>): Ref<number> {
  const width = ref(720);
  let observer: ResizeObserver | undefined;
  onMounted(() => {
    if (!element.value) return;
    const measure = (): void => {
      if(element.value) width.value=Math.max(240,element.value.getBoundingClientRect().width);
    };
    measure();
    observer=new ResizeObserver(measure); observer.observe(element.value);
  });
  onBeforeUnmount(()=>observer?.disconnect());
  return width;
}
