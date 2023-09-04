using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;
using System.Threading;
using UnityEditor;
using UnityEngine;
using Debug = UnityEngine.Debug;

public class Text3DMaker : EditorWindow
{
    private static bool IsUpmPackage = false;

    const string PackagePath = "Packages/com.metaaaa.text3dmaker/";
    private const string UserSettingsConfigKeyPrefix = "Text3DMaker_";
    private string _blenderPath = "";
    private string _dirname = "";
    private string _fontpath = "C:/Windows/Fonts/meiryo.ttc";
    private string _text = "";
    private float _extrude = 0;
    private float _offset = 0;
    private float _bevel_depth = 0;
    private int _bevel_resolution = 0;
    private float _spacing = 0.1f;
    private List<Vector3> _originOffsets = new List<Vector3>();

    [MenuItem("metaaa/Text3DMaker")]
    static void Create()
    {
        var window = GetWindow<Text3DMaker>("Text3DMaker");

        window._blenderPath =
            EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_blenderPath))) ?? window._blenderPath;
        window._fontpath = EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_fontpath))) ?? window._fontpath;
        window._text = EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_text))) ?? window._text;
        window._dirname = EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_dirname))) ?? window._dirname;
        window._extrude = (float)Convert.ToDouble(EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_extrude))));
        window._offset = (float)Convert.ToDouble(EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_offset))));
        window._bevel_depth =
            (float)Convert.ToDouble(EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_bevel_depth))));
        window._bevel_resolution =
            Convert.ToInt32(EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_bevel_resolution))));
        window._spacing = (float)Convert.ToDouble(EditorUserSettings.GetConfigValue(GetConfigKey(nameof(_spacing))));
    }

    private void OnDisable()
    {
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_blenderPath)), _blenderPath);
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_fontpath)), _fontpath);
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_text)), _text);
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_dirname)), _dirname);
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_extrude)),
            _extrude.ToString(Thread.CurrentThread.CurrentCulture));
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_offset)),
            _offset.ToString(Thread.CurrentThread.CurrentCulture));
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_bevel_depth)),
            _bevel_depth.ToString(Thread.CurrentThread.CurrentCulture));
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_bevel_resolution)),
            _bevel_resolution.ToString(Thread.CurrentThread.CurrentCulture));
        EditorUserSettings.SetConfigValue(GetConfigKey(nameof(_spacing)),
            _spacing.ToString(Thread.CurrentThread.CurrentCulture));
    }

    private void OnGUI()
    {
        try
        {
            var folderIcon = EditorGUIUtility.IconContent("Folder ICon");
            var folderIconStyle = new GUIStyle { fixedHeight = 20, fixedWidth = 20 };

            using (new EditorGUILayout.HorizontalScope())
            {
                using (new EditorGUI.DisabledScope(true))
                {
                    EditorGUILayout.TextField("Blender exe path", _blenderPath);
                }

                if (GUILayout.Button(folderIcon, folderIconStyle))
                {
                    _blenderPath =
                        EditorUtility.OpenFilePanelWithFilters("select Blender exe", "", new[] { "Exe", "exe" });
                }
            }

            using (new EditorGUILayout.HorizontalScope())
            {
                using (new EditorGUI.DisabledScope(true))
                {
                    EditorGUILayout.TextField("Export path", _dirname);
                }

                if (GUILayout.Button(folderIcon, folderIconStyle))
                {
                    _dirname = EditorUtility.OpenFolderPanel("select folder", "", "");
                }
            }

            _fontpath = EditorGUILayout.TextField("Font File", _fontpath);
            _text = EditorGUILayout.TextField("text", _text);

            _extrude = EditorGUILayout.FloatField("extrude", _extrude);
            _offset = EditorGUILayout.FloatField("offset", _offset);
            _bevel_depth = EditorGUILayout.FloatField("bevel_depth", _bevel_depth);

            _bevel_resolution = EditorGUILayout.IntField("bevel_resolution", _bevel_resolution);
            _spacing = EditorGUILayout.FloatField("char spacing", _spacing);

            if (GUILayout.Button("process")) Make();
        }
        catch (System.FormatException)
        {
        }
    }

    private static string GetConfigKey(string varName)
    {
        return UserSettingsConfigKeyPrefix + varName;
    }

    private void Make()
    {
        var sb = new StringBuilder(" --background --python ");
        sb.Append(PackagePathResolver("/Editor/Tools~/3DTextMakerAddOn.py"));
        sb.Append(" --");
        sb.Append($" --text \"{_text}\"");
        sb.Append($" --fontpath \"{_fontpath}\"");
        sb.Append($" --extrude {_extrude.ToString(Thread.CurrentThread.CurrentCulture)}");
        sb.Append($" --offset {_offset.ToString(Thread.CurrentThread.CurrentCulture)}");
        sb.Append($" --bevel_depth {_bevel_depth.ToString(Thread.CurrentThread.CurrentCulture)}");
        sb.Append($" --bevel_resolution {_bevel_resolution.ToString(Thread.CurrentThread.CurrentCulture)}");
        sb.Append($" --dirname \"{_dirname}\"");
        ExecCommand(_blenderPath, sb.ToString());

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        SavePrefab();
    }

    private void SavePrefab()
    {
        var root = new GameObject();
        var rootTra = root.transform;

        var basePath = _dirname + "/" + _text + "/";
        var fileBasePath = basePath + _text + "_";

        var offsetX = 0f;
        for (int i = 0; i < _text.Length; i++)
        {
            var textObj = AssetDatabase.LoadAssetAtPath<GameObject>(AbsoluteToAssetsPath(fileBasePath + i + ".fbx"));
            var mesh = textObj.GetComponent<MeshFilter>().sharedMesh;
            mesh.RecalculateBounds();
            var bounds = mesh.bounds;
            var boundSize = Vector3.Scale(bounds.size, textObj.transform.localScale);
            textObj = Instantiate(textObj, rootTra);
            var originOffset = _originOffsets[i];
            textObj.transform.position = new Vector3(offsetX - originOffset.x, originOffset.y, 0);
            offsetX -= boundSize.x + _spacing;
        }

        PrefabUtility.SaveAsPrefabAssetAndConnect(root, Path.Combine(basePath, _text + ".prefab"),
            InteractionMode.UserAction);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        DestroyImmediate(root);
    }

    private string AbsoluteToAssetsPath(string self)
    {
        return self.Replace("\\", "/").Replace(Application.dataPath, "Assets");
    }

    private string PackagePathResolver(string path)
    {
        string absolute = "";
        if (IsUpmPackage)
            absolute = Path.GetFullPath(PackagePath + path);
        else
            absolute = Application.dataPath + "/Src" + path;
        return absolute;
    }

    private void ExecCommand(string exePath, string arguments)
    {
        ProcessStartInfo startInfo = new ProcessStartInfo()
        {
            FileName = exePath,
            Arguments = arguments,
            WindowStyle = ProcessWindowStyle.Hidden,
            UseShellExecute = false,
            RedirectStandardOutput = true,
        };

        // プロセスを起動する。
        using (Process process = Process.Start(startInfo))
        {
            Debug.Log("\"" + _blenderPath + "\"" + arguments);
            string allLine = "";
            string newLine = "";
            
            _originOffsets.Clear();
            while ((newLine = process?.StandardOutput.ReadLine()) != null)
            {
                allLine += newLine + "\n";
                var offsets = newLine.Split(',');
                if (offsets[0] == "origin_offset")
                {
                    var vec = new Vector3(
                        float.Parse(offsets[1], CultureInfo.InvariantCulture.NumberFormat),
                        float.Parse(offsets[2], CultureInfo.InvariantCulture.NumberFormat),
                        float.Parse(offsets[3], CultureInfo.InvariantCulture.NumberFormat)
                    );
                    _originOffsets.Add(vec);
                }
            }
            Debug.Log(allLine);
            process?.StandardOutput.ReadToEnd();
            process?.WaitForExit(1000);
        }
    }
}