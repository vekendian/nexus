// An importable module: Java methods callable from Lua.
//
//   javac -cp build/module-api.jar -d build/zip-import examples/import/zip.java
//   d8 --min-api 21 --output build/zip-dex build/zip-import/zip.class
//   （d8 writes build/zip-dex/classes.dex. Import accepts two packagings:）
//
//   as a jar  :  zip -j /sdcard/Download/zip.jar build/zip-dex/classes.dex
//                （the archive must contain a classes.dex entry -- that is
//                  the whole jar; no META-INF is needed）
//   as a dex  :  cp build/zip-dex/classes.dex /sdcard/Download/zip.dex
//                （the raw dex IS the module file, like examples/module above）
//
// Install from Lua and use it:
//
//   nexus.modules.install("/sdcard/Download/zip.jar")
//   local zip = nexus.modules.import("zip")
//   print(zip.compress("/sdcard/SomeFolder", 5))
//   print(zip.decompress("/sdcard/Download/SomeFolder.zip", "/sdcard/Restored"))
//
// What makes the methods visible: @Export on the entry class. The entry class
// is whoever in the archive carries @ModuleManifest -- here `zip`, found by
// the loader without any name in the manifest. Do NOT write entry(): the
// discovered binary name is used instead, and a bare name like "Zip" would
// fail a loadClass lookup (the manifest field takes the full dotted name when
// it is set at all). One archive, one entry class: the annotation scanner
// stops at the first manifest it finds, top-level classes only.
//
// Method shaping for the Lua side:
//   - public, instance methods on the entry class
//   - parameter types map p=String i=int/long n=double/float b=boolean
//     a=String[] varargs (last parameter only); separate them positionally
//   - return types map v=void s=String n=number b=boolean; unknown types are
//     received in Lua as strings (toString)
//   - a thrown exception reaches Lua as (nil, message)
//
// These two return String on purpose: a "..." error message is friendlier
// through Lua than a thrown exception, and "ok" reads either way.

import org.vekendian.nexus.api.Export;
import org.vekendian.nexus.api.ModuleManifest;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

@ModuleManifest(name = "Zip",
                   description = "folder <-> zip, callable from Lua",
                   version = 1,
                   autostart = false)
public class zip {

    @Export("compress")
    public String compress(String folderPath, int level) throws IOException {
        File folder = new File(folderPath);
        if (!folder.isDirectory()) {
            return "error: not a folder: " + folderPath;
        }
        File out = new File(folder.getParentFile(), folder.getName() + ".zip");
        ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(out));
        try {
            zip.setLevel(level < 0 || level > 9 ? 5 : level);
            add(zip, folder, "");
        } finally {
            zip.close();
        }
        return "ok: " + out.getAbsolutePath();
    }

    @Export("decompress")
    public String decompress(String zipPath, String destDir) throws IOException {
        File dest = new File(destDir);
        if (!dest.isDirectory() && !dest.mkdirs()) {
            return "error: cannot create " + destDir;
        }
        String canonical = dest.getCanonicalPath() + File.separator;
        ZipInputStream zip = new ZipInputStream(
                new BufferedInputStream(new FileInputStream(zipPath)));
        try {
            byte[] buf = new byte[65536];
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                File out = new File(dest, entry.getName());
                // stay inside destDir: an archive with ../ entries unpacks
                // to exactly what it names, nothing above it
                if (!out.getCanonicalPath().startsWith(canonical)) {
                    return "error: refusing path outside destination: " + entry.getName();
                }
                if (entry.isDirectory()) {
                    out.mkdirs();
                    continue;
                }
                out.getParentFile().mkdirs();
                BufferedOutputStream write = new BufferedOutputStream(
                        new FileOutputStream(out));
                try {
                    int n;
                    while ((n = zip.read(buf)) > 0) {
                        write.write(buf, 0, n);
                    }
                } finally {
                    write.close();
                }
                zip.closeEntry();
            }
        } finally {
            zip.close();
        }
        return "ok: " + dest.getAbsolutePath();
    }

    private void add(ZipOutputStream zip, File file, String prefix) throws IOException {
        String name = prefix + file.getName() + (file.isDirectory() ? "/" : "");
        if (file.isDirectory()) {
            zip.putNextEntry(new ZipEntry(name));
            zip.closeEntry();
            File[] kids = file.listFiles();
            if (kids != null) {
                for (File kid : kids) {
                    add(zip, kid, name);
                }
            }
            return;
        }
        zip.putNextEntry(new ZipEntry(name));
        BufferedInputStream in = new BufferedInputStream(new FileInputStream(file));
        try {
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) {
                zip.write(buf, 0, n);
            }
        } finally {
            in.close();
        }
        zip.closeEntry();
    }
}
