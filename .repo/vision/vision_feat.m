// 用 macOS Vision 框架的 VNGenerateImageFeaturePrintRequest 计算图像特征向量。
// 系统自带模型：零 Python 依赖、零下载、完全离线。
//
// 用法：
//   vision_feat <image>            单张，输出 DIM / VEC 两行
//   vision_feat -                  批量，从 stdin 逐行读路径（空行与 # 开头跳过）
//
// 批量模式每条结果三行，便于解析：
//   === <path>
//   DIM 768
//   VEC f0 f1 ...
// 读取失败则输出 `ERROR <path> <原因>`，不中断后续。
#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <Vision/Vision.h>

static BOOL emit(NSString *path) {
    NSImage *img = [[NSImage alloc] initWithContentsOfFile:path];
    if (!img) { printf("ERROR %s load\n", path.UTF8String); return NO; }
    CGImageRef cg = [img CGImageForProposedRect:NULL context:nil hints:nil];
    if (!cg) { printf("ERROR %s cgimage\n", path.UTF8String); return NO; }

    VNGenerateImageFeaturePrintRequest *req =
        [[VNGenerateImageFeaturePrintRequest alloc] init];
    req.imageCropAndScaleOption = VNImageCropAndScaleOptionCenterCrop;
    VNImageRequestHandler *h =
        [[VNImageRequestHandler alloc] initWithCGImage:cg options:@{}];
    NSError *err = nil;
    if (![h performRequests:@[req] error:&err]) {
        printf("ERROR %s %s\n", path.UTF8String,
               err.localizedDescription ? err.localizedDescription.UTF8String : "perform");
        return NO;
    }
    VNFeaturePrintObservation *obs = (VNFeaturePrintObservation *)req.results.firstObject;
    if (!obs) { printf("ERROR %s noresult\n", path.UTF8String); return NO; }

    printf("=== %s\n", path.UTF8String);
    printf("DIM %lu\n", (unsigned long)obs.elementCount);
    const float *f = (const float *)obs.data.bytes;
    NSUInteger n = obs.data.length / sizeof(float);
    printf("VEC");
    for (NSUInteger i = 0; i < n; i++) printf(" %.6f", f[i]);
    printf("\n");
    return YES;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc < 2) { fprintf(stderr, "usage: vision_feat <image> | -\n"); return 2; }

        if (strcmp(argv[1], "-") == 0) {
            // 批量：stdin 逐行读路径。
            // 372 张图逐个起进程约 19 秒，一个进程批量跑能省掉几乎全部开销。
            char line[4096];
            while (fgets(line, sizeof(line), stdin)) {
                size_t len = strlen(line);
                while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = 0;
                if (len == 0 || line[0] == '#') continue;
                @autoreleasepool {
                    emit([NSString stringWithUTF8String:line]);
                }
                fflush(stdout);      // 逐条刷新，Python 端可流式读取
            }
            return 0;
        }

        for (int i = 1; i < argc; i++) {
            @autoreleasepool {
                emit([NSString stringWithUTF8String:argv[i]]);
            }
        }
    }
    return 0;
}
