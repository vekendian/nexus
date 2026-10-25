// dex -> smali, using the baksmali that ships inside the pinned apktool jar.
//
// Why this file exists: apktool-2.8.1.jar bundles com.android.tools.smali.baksmali,
// but its Main class is a jcommander Command with no static main(), so
// `java -cp apktool.jar com.android.tools.smali.baksmali.Main` fails with
// "Main method not found". The library entry point is public though, so three
// lines against the same jar do the job and add no new dependency.
//
//   javac -cp <apktool.jar> -d build/tools tools/BaksmaliDriver.java
//   java -cp build/tools:<apktool.jar> BaksmaliDriver <in.dex> <outDir> [api]
//
// The API level only affects the version header baksmali writes; the opcode set
// is the same for everything DEX 035 covers.

import com.android.tools.smali.baksmali.Baksmali;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.dexlib2.DexFileFactory;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.iface.DexFile;
import com.android.tools.smali.dexlib2.iface.MultiDexContainer;

import java.io.File;
import java.util.List;

public final class BaksmaliDriver {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: BaksmaliDriver <in.dex> <outDir> [api]");
            System.exit(2);
        }
        File in = new File(args[0]);
        File out = new File(args[1]);
        int api = args.length > 2 ? Integer.parseInt(args[2]) : 21;
        if (!in.isFile()) {
            System.err.println("no such dex: " + in);
            System.exit(2);
        }
        // This apktool build exposes only loadDexContainer (loadDexFile is
        // absent), so take the first entry out of the container by name.
        MultiDexContainer<? extends DexFile> container =
                DexFileFactory.loadDexContainer(in, Opcodes.forApi(api));
        List<String> names = container.getDexEntryNames();
        if (names.isEmpty()) {
            System.err.println("no dex entry in " + in);
            System.exit(1);
        }
        DexFile dex = container.getEntry(names.get(0)).getDexFile();
        if (!Baksmali.disassembleDexFile(dex, out, api, new BaksmaliOptions())) {
            System.err.println("baksmali failed for " + in);
            System.exit(1);
        }
        System.out.println("disassembled " + in + " -> " + out);
    }
}